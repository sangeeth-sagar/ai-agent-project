# app/core/memory.py
import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# 1. Setup Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", 
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 2. Setup ChromaDB
vector_store = Chroma(
    collection_name="chat_memory",
    embedding_function=embeddings,
    persist_directory="./chroma_db" 
)

def save_memory(user_id: str, chat_id: str, text: str):
    """Saves user input into the vector DB."""
    doc = Document(
        page_content=text,
        metadata={"user_id": user_id, "chat_id": chat_id}
    )
    vector_store.add_documents([doc])

def retrieve_memory(user_id: str, query: str, current_chat_id: str, k: int = 3):
    """
    Hybrid Search Strategy with FIXED Syntax.
    """
    # Attempt 1: Strict Local Search (Current Chat Only)
    # FIX: We use "$and" because we are filtering by TWO fields (user_id AND chat_id)
    local_filter = {
        "$and": [
            {"user_id": user_id},
            {"chat_id": current_chat_id}
        ]
    }
    
    local_results = vector_store.similarity_search(
        query, 
        k=k, 
        filter=local_filter # <--- Passing the fixed filter
    )
    
    # If we found good matches locally, return them
    if local_results:
        return [doc.page_content for doc in local_results]
        
    # Attempt 2: Global Search (Backup)
    # This filter is fine because it only has ONE field
    global_results = vector_store.similarity_search(
        query, 
        k=k, 
        filter={"user_id": user_id}
    )
    
    return [f"{doc.page_content} (from another chat)" for doc in global_results]