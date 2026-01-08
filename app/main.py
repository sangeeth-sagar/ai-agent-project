# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the pool we created in database.py
from app.core.database import pool 

# Import Routers
from app.routers import auth, chat

# --- LIFECYCLE MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Open the Database Pool
    print("🚀 Starting up: Connecting to Database...")
    await pool.open()
    yield
    # 2. Shutdown: Close the Database Pool
    print("🛑 Shutting down: Closing Database connection...")
    await pool.close()

# --- APP SETUP ---
app = FastAPI(
    title="AI Agent API", 
    lifespan=lifespan # <--- Attach the lifecycle here
)

# CORS (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev. Change to ["http://localhost:5173"] for prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCLUDE ROUTERS ---
app.include_router(auth.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "AI Agent Backend is Running 🚀"}