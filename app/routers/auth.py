# app/routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.core.database import get_db_connection
from app.core.security import get_password_hash, verify_password, create_access_token
import uuid
from app.models.models import User
from app.routers.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Pydantic Models ---
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in_minutes: int

# --- Signup Endpoint ---
@router.post("/signup")
async def signup(user: UserSignup, conn = Depends(get_db_connection)):
    hash_pw = get_password_hash(user.password)
    
    # Generate the ID manually to avoid DB "Not Null" errors
    new_user_id = str(uuid.uuid4()) 

    try:
        async with conn.cursor() as cur:
            # 1. Check if email exists
            await cur.execute("SELECT user_id FROM users WHERE email = %s", (user.email,))
            if await cur.fetchone():
                raise HTTPException(status_code=400, detail="Email already registered")

            # 2. Check if username exists
            await cur.execute("SELECT user_id FROM users WHERE username = %s", (user.username,))
            if await cur.fetchone():
                raise HTTPException(status_code=400, detail="Username already taken")

            # 3. Insert User
            await cur.execute(
                """
                INSERT INTO users (user_id, username, email, hashed_password, is_active) 
                VALUES (%s, %s, %s, %s, TRUE) 
                RETURNING user_id, username
                """,
                (new_user_id, user.username, user.email, hash_pw) 
            )
            
            created_user = await cur.fetchone()
            await conn.commit() 
            
            return {"msg": "User created", "user_id": str(created_user[0]), "username": created_user[1]}
            
    except Exception as e:
        await conn.rollback()
        if isinstance(e, HTTPException): raise e
        print(f"Signup Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    

# --- Login Endpoint ---
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), conn = Depends(get_db_connection)):
    """
    Standard OAuth2 Login. 
    Accepts 'username' (which acts as email here) and 'password'.
    """
    async with conn.cursor() as cur:
        # 1. Fetch User (Allow login by Email OR Username for better UX)
        await cur.execute(
            """
            SELECT user_id, hashed_password 
            FROM users 
            WHERE email = %s OR username = %s
            """, 
            (form_data.username, form_data.username)
        )
        user = await cur.fetchone()

        # 2. Verify
        if not user or not verify_password(form_data.password, user[1]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 3. Create Token
        # CRITICAL FIX: Storing user_id in 'sub' so deps.py can find the user later
        user_id = str(user[0])
        access_token = create_access_token(data={"sub": user_id})

        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "expires_in_minutes": 30 # Default from security.py
        }


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns the current user's profile information.
    Used by Frontend to show name/email in the UI.
    """
    return {
        "user_id": str(current_user.user_id),
        "username": current_user.username,
        "email": current_user.email
    }