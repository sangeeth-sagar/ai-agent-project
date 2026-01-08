# app/routers/deps.py
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
# Ensure this import matches your actual file structure
from app.models.models import User 

# Settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

# --- CRITICAL FIX: Point to the actual login endpoint ---
# This tells Swagger: "Send the username/password to /auth/login"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. Get Current User (Full Object) ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Note: Ensure your create_access_token uses "sub" for the user ID/username
        # If your auth.py puts user_id in "sub", change this logic accordingly.
        # Assuming "sub" holds the USER_ID (string):
        user_identifier: str = payload.get("sub")
        
        if user_identifier is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Fetch user from Postgres
    # NOTE: If your token stores ID in 'sub', search by ID. 
    # If it stores username, search by username.
    # Based on your auth.py, you saved user_id as 'sub'.
    user = db.query(User).filter(User.user_id == user_identifier).first()
    
    if user is None:
        raise credentials_exception

    # CHECK IS_ACTIVE (Security)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user

# --- 2. Get Current User ID (Lightweight version) ---
async def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    return str(current_user.user_id)