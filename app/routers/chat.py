# app/routers/chat.py
import re
import uuid
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from langchain_core.messages import HumanMessage, AIMessage

# Import your modules
from app.routers.deps import get_current_user_id
from app.core.database import get_db_connection
from app.core.prompts import PERSONALITY_PROMPTS
from app.agent.workflow import app_graph

router = APIRouter(prefix="/chat", tags=["Chat"])

# --- 1. SANITIZATION HELPER (Allows Emojis ✅) ---
def sanitize_text(text: str) -> str:
    """
    Cleans input text:
    1. Removes leading/trailing whitespace.
    2. Removes invisible control characters (like null bytes) that break databases.
    3. KEEPS Emojis and international characters.
    """
    if not text:
        return ""
        
    text = text.strip()
    
    # Remove ONLY invisible control characters (ASCII 0-31) 
    # except newline (\n) and tab (\t)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text

# --- 2. REQUEST MODELS ---
class CreateChatRequest(BaseModel):
    chat_name: str
    personality: str 

    @field_validator('personality')
    def validate_personality(cls, v):
        key = v.lower()
        if key not in PERSONALITY_PROMPTS:
            allowed = ", ".join(PERSONALITY_PROMPTS.keys())
            raise ValueError(f"Invalid personality. Allowed types: {allowed}")
        return key

class ChatRequest(BaseModel):
    chat_id: str
    message: str

# --- 3. DATABASE HELPERS ---
async def save_message(conn, chat_id: str, role: str, content: str):
    """Inserts a message row into Postgres."""

    new_id=str(uuid.uuid4())
    async with conn.cursor() as cur:
        await cur.execute(
            """
            INSERT INTO messages (id, chat_id, role, content)
            VALUES (%s, %s, %s, %s)
            """,
            (new_id, chat_id, role, content)
        )
        await conn.commit()

async def get_chat_history(conn, chat_id: str, limit: int = 10):
    """Fetches the last N messages for context."""
    async with conn.cursor() as cur:
        await cur.execute(
            """
            SELECT role, content FROM messages 
            WHERE chat_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s
            """,
            (chat_id, limit)
        )
        rows = await cur.fetchall()
        
    # Reverse to get chronological order [Oldest -> Newest]
    history = []
    for role, content in rows[::-1]:
        if role == 'user':
            history.append(HumanMessage(content=content))
        elif role == 'ai':
            history.append(AIMessage(content=content))
            
    return history

# --- 4. API ENDPOINTS ---

@router.post("/new")
async def create_new_chat(
    payload: CreateChatRequest,
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_db_connection)
):
    system_prompt = PERSONALITY_PROMPTS[payload.personality]
    
    async with conn.cursor() as cur:
        # Check for duplicates
        await cur.execute(
            "SELECT chat_id FROM chats WHERE user_id = %s AND chat_name = %s", 
            (user_id, payload.chat_name)
        )
        if await cur.fetchone():
            raise HTTPException(status_code=400, detail="Chat name already exists")

        new_chat_id = str(uuid.uuid4()) 

        # Create Chat
        await cur.execute(
            """
            INSERT INTO chats (chat_id, user_id, chat_name, personality_type, system_prompt) 
            VALUES (%s, %s, %s, %s, %s) 
            RETURNING chat_id
            """,
            (new_chat_id, user_id, payload.chat_name, payload.personality, system_prompt)
        )
        new_chat = await cur.fetchone()
        await conn.commit() 
        
    return {
        "msg": "Chat created", 
        "chat_id": str(new_chat[0]), 
        "mode": payload.personality
    }

@router.post("/send")
async def send_message(
    payload: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_db_connection)
):
    # A. CLEAN INPUT (Safe for DB)
    clean_content = sanitize_text(payload.message)
    
    if not clean_content:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # B. VERIFY CHAT OWNERSHIP
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT system_prompt FROM chats WHERE chat_id = %s AND user_id = %s",
            (payload.chat_id, user_id)
        )
        chat_data = await cur.fetchone()
    
    if not chat_data:
        raise HTTPException(status_code=404, detail="Chat not found or access denied")
    
    system_instruction = chat_data[0]

    # C. SAVE USER MESSAGE (Postgres - Short Term)
    await save_message(conn, payload.chat_id, "user", clean_content)

    # D. FETCH RECENT HISTORY
    history_messages = await get_chat_history(conn, payload.chat_id, limit=10)

    # E. RUN GRAPH (The Brain)
    # --- CRITICAL FIX: We pass 'chat_id' here so ChromaDB knows where to look ---
    inputs = {
        "messages": history_messages, 
        "user_id": user_id,
        "chat_id": payload.chat_id, # <--- THIS LINE FIXES THE CHROMA ERROR
        "system_instruction": system_instruction
    }
    
    config = {"configurable": {"thread_id": payload.chat_id}}
    
    # Call Gemini
    result = await app_graph.ainvoke(inputs, config=config)
    
    # F. SAVE AI RESPONSE
    ai_reply_text = result["messages"][-1].content
    await save_message(conn, payload.chat_id, "ai", ai_reply_text)
    
    return {"reply": ai_reply_text}


# app/routers/chat.py
# ... (Keep all your existing imports and code) ...

# --- NEW: Endpoint 3 - Get All Chats (For Sidebar) ---
@router.get("/all")
async def get_all_chats(
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_db_connection)
):
    async with conn.cursor() as cur:
        # Get ID, Name, and Mode (Personality)
        await cur.execute(
            """
            SELECT chat_id, chat_name, personality_type, created_at 
            FROM chats 
            WHERE user_id = %s 
            ORDER BY created_at DESC
            """, 
            (user_id,)
        )
        rows = await cur.fetchall()
    
    # Format for JSON response
    chats = []
    for row in rows:
        chats.append({
            "chat_id": str(row[0]),
            "chat_name": row[1],
            "mode": row[2],
            "created_at": row[3]
        })
    return chats

# --- NEW: Endpoint 4 - Get Specific Chat History (For Chat Window) ---
@router.get("/{chat_id}")
async def get_chat_details(
    chat_id: str,
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_db_connection)
):
    
    try:
        real_uuid = UUID(chat_id)
    except ValueError:
        # If frontend sends "undefined" or garbage, return 400 instead of crashing
        raise HTTPException(status_code=400, detail="Invalid Chat ID format")
    # 1. Verify Chat Belongs to User
    async with conn.cursor() as cur:
        await cur.execute(
            "SELECT chat_name, personality_type FROM chats WHERE chat_id = %s AND user_id = %s",
            (chat_id, user_id)
        )
        chat_info = await cur.fetchone()
        
        if not chat_info:
            raise HTTPException(status_code=404, detail="Chat not found")

        # 2. Get Messages (All history for UI)
        await cur.execute(
            """
            SELECT role, content, created_at 
            FROM messages 
            WHERE chat_id = %s 
            ORDER BY created_at ASC 
            """, 
            (chat_id,)
        )
        msg_rows = await cur.fetchall()

    messages = [
        {"role": r[0], "content": r[1], "time": r[2]} 
        for r in msg_rows
    ]

    return {
        "chat_id": chat_id,
        "chat_name": chat_info[0],
        "mode": chat_info[1],
        "messages": messages
    }

# --- NEW: Endpoint 5 - Delete Chat (Optional but useful) ---
@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    user_id: str = Depends(get_current_user_id),
    conn = Depends(get_db_connection)
):
    async with conn.cursor() as cur:
        # Verify ownership
        await cur.execute("SELECT 1 FROM chats WHERE chat_id = %s AND user_id = %s", (chat_id, user_id))
        if not await cur.fetchone():
            raise HTTPException(status_code=404, detail="Chat not found")
            
        # Delete (Cascade will handle messages automatically if configured, but let's be safe)
        await cur.execute("DELETE FROM messages WHERE chat_id = %s", (chat_id,))
        await cur.execute("DELETE FROM chats WHERE chat_id = %s", (chat_id,))
        await conn.commit()
        
    return {"msg": "Chat deleted successfully"}