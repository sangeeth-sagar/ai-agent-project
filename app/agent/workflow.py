# app/agent/workflow.py
import os
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, BaseMessage
from app.core.memory import retrieve_memory, save_memory # <--- NEW: Import Memory Tools
import operator

load_dotenv()

# --- 1. SETUP GEMINI MODEL ---
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("GOOGLE_API_KEY not found in .env file")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.7,
    max_retries=2,
)

# --- 2. DEFINE STATE ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add] 
    user_id: str
    chat_id: str # <--- NEW: We need this to filter memory by chat
    system_instruction: str

# --- 3. DEFINE NODES ---
async def call_gemini(state: AgentState):
    """
    The Brain Node: Retrieves Memory -> Thinks -> Replies -> Saves Memory
    """
    user_id = state["user_id"]
    chat_id = state["chat_id"]
    
    # 1. GET USER INPUT
    # We grab the last message (the one the user just sent)
    last_user_msg = state["messages"][-1].content
    
    # 2. RETRIEVE MEMORY (Hybrid Search)
    # Checks current chat first, then checks other chats if needed.
    past_memories = retrieve_memory(user_id, last_user_msg, chat_id)
    
    # Format the memories into a text block for the AI
    memory_text = ""
    if past_memories:
        memory_text = "\nRELEVANT MEMORIES FROM PAST:\n" + "\n".join([f"- {m}" for m in past_memories])

    # 3. AUGMENT THE SYSTEM PROMPT
    # We inject the retrieved memories into the instructions
    final_system_prompt = (
        f"{state['system_instruction']}\n"
        f"----------------\n"
        f"{memory_text}\n"
        f"----------------\n"
        "Use the memories above to answer if they are relevant. If not, ignore them."
    )
    
    # 4. CALL AI
    # We replace the static system prompt with our dynamic, memory-filled one
    # Note: We reconstruct the prompt list: [System Message] + [Conversation History]
    prompt_messages = [SystemMessage(content=final_system_prompt)] + state["messages"]
    
    response = await llm.ainvoke(prompt_messages)
    
    # 5. SAVE MEMORY (Fire and Forget)
    # We save what the user said so we remember it next time
    save_memory(user_id, chat_id, last_user_msg)
    
    return {"messages": [response]}

# --- 4. BUILD GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_gemini)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app_graph = workflow.compile()