# app/core/db_init.py
from psycopg_pool import AsyncConnectionPool

async def init_db(pool: AsyncConnectionPool):
    """
    Creates tables automatically.
    NOTE: We temporarily disabled Vector/Memory tables to fix the Windows error.
    """
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            # 1. Enable UUID Extension (Keep this!)
            await cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
            
            # --- TEMPORARILY DISABLED VECTOR EXTENSION ---
            # await cur.execute('CREATE EXTENSION IF NOT EXISTS vector;')
            
            # 2. Users Table
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
            """)

            # 3. Chats Table
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                chat_name VARCHAR(100) NOT NULL,
                personality_type VARCHAR(50) NOT NULL,
                system_prompt TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                last_active_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, chat_name)
            );
            """)

            # 4. Messages Table
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                chat_id UUID NOT NULL REFERENCES chats(chat_id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL, 
                content TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
            """)
            await cur.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_time ON messages(chat_id, created_at DESC);")

            # --- TEMPORARILY DISABLED MEMORY TABLE ---
            # Because 'vector(1536)' type doesn't exist on your PC yet.
            # await cur.execute("""
            # CREATE TABLE IF NOT EXISTS long_term_memories (
            #     memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            #     user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            #     chat_id UUID REFERENCES chats(chat_id) ON DELETE SET NULL,
            #     summary_text TEXT NOT NULL,
            #     embedding vector(1536),
            #     created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            # );
            # """)

            print("✅ Database tables checked/created (Vector skipped).")