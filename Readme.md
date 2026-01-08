# 🤖 Full Stack AI Agent 

A modern, persistent AI Chatbot built with **FastAPI**, **React**, and **LangGraph**. Designed to replicate the experience of Google Gemini with multiple AI personalities, secure authentication, and long-term memory.

## 🚀 Features

* **🤖 Multi-Persona AI:** Switch between "Friend", "Girlfriend", "Bully", etc.
* **🧠 Agentic Workflow:** Uses **LangGraph** to manage conversation state and logic.
* **🔐 Secure Authentication:** Complete Login/Signup system using **JWT** (JSON Web Tokens) and **Bcrypt** hashing.
* **💾 Persistent Memory:** Stores users, chat sessions, and message history in **PostgreSQL** and     **ChromaDB**.
* **🎨 Modern UI:** Responsive React frontend styled with **Tailwind CSS** (Gemini-inspired design).
* **⚡ Real-time Performance:** Optimistic UI updates for an instant chat experience.

## 🛠️ Tech Stack

* **Frontend:** React, TypeScript, Tailwind CSS, Axios.
* **Backend:** FastAPI, Python, LangGraph, LangChain.
* **AI Model:** Google Gemini 1.5 Flash (via Google GenAI).
* **Database:** PostgreSQL (SQLAlchemy ORM),ChromaDB.
* **Security:** OAuth2 (Password Flow), Passlib, Python-Jose.

## ⚙️ Installation & Setup

### Prerequisites
* Python 3.10+
* Node.js & npm
* PostgreSQL installed and running

### 1. Backend Setup
```bash
# Clone the repo
git clone [https://github.com/sangeeth-sagar/ai-agent-project.git](https://github.com/sangeeth-sagar/ai-agent-project.git)
cd ai-agent-project/backend

# Create virtual env
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DATABASE_URL=postgresql://user:password@localhost/dbname" > .env
echo "GOOGLE_API_KEY=your_gemini_key" >> .env
echo "SECRET_KEY=your_secret_key" >> .env

# Run Server
uvicorn app.main:app --reload
2. Frontend Setup
Bash

cd ../frontend

# Install dependencies
npm install

# Run React App
npm run dev
📸 Video Demo
(https://drive.google.com/file/d/1oddkU2HhoW_OVDKwdCkRYky7s0ckDyYr/view?usp=sharing)



