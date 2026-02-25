from app.main import app  # Adjust this path to wherever your FastAPI 'app' object is defined

# Vercel requires the app object to be available at the module level
# No need for uvicorn.run() here