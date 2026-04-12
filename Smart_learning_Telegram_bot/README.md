# Smart Learning Bot 🤖📚

> An AI-powered academic learning system that converts university syllabus into a structured daily study roadmap using Groq LLM, MCP-style tool calling, FastAPI backend, PostgreSQL, and Telegram bot automation.

---

# 🎯 Problem Statement

Students struggle not because content is hard, but because:

- No structured daily study plan
- No syllabus breakdown into tasks
- No progress tracking system
- No feedback or accountability loop

Smart Learning Bot solves this by turning any syllabus into a **guided AI-driven learning roadmap with tracking and evaluation**.

---

# 🚀 Solution

This system acts as an AI academic assistant that:

- Converts syllabus into daily tasks
- Assigns structured learning goals
- Tracks student progress
- Provides marks/feedback for completed tasks
- Adapts learning flow based on performance
- Delivers everything via Telegram bot

---

# 🧠 System Architecture

User (Telegram)
↓
bot.py (Telegram Interface)
↓
ai_tutor.py (Groq LLM - Planning & Reasoning)
↓
mcp_server.py (FastAPI Tool Execution Layer)
↓
mcp_tools.py (Tool Registry)
↓
services.py (Business Logic Layer)
↓
database.py (PostgreSQL Connection)
↓
PostgreSQL (Data Storage)

---

# 📁 Project Structure

smart_learning_bot/
│
├── bot.py              # Telegram bot interface
├── ai_tutor.py         # AI roadmap + tutor logic (Groq LLM)
├── mcp_server.py       # MCP tool execution server (FastAPI)
├── mcp_tools.py       # Tool functions for AI execution
├── services.py         # Business logic (roadmap + tracking)
├── database.py         # PostgreSQL connection setup
├── models.py           # Database schema (students, tasks, progress)
├── config.py           # Environment configuration
├── main.py             # Application entry point
├── req.txt             # Dependencies
└── .env                # Environment variables

---

# ⚙️ Tech Stack

## AI Layer
- Groq LLM (Syllabus understanding + learning planner)

## Backend Layer
- FastAPI (MCP tool execution server)
- Python 3.10+

## Bot Layer
- python-telegram-bot==20.7

## Data Layer
- PostgreSQL
- SQLAlchemy ORM

## System Design
- MCP-style tool calling architecture
- Service-based modular backend

---

# 📦 Dependencies

python-telegram-bot==20.7  
sqlalchemy  
psycopg2-binary  
python-dotenv  
fastapi  
uvicorn  
groq  
requests  

---

# 🧠 Key Features

## 📚 AI Syllabus Planner
- Converts syllabus into structured daily roadmap
- Breaks topics into learning tasks
- Generates study sequence automatically

## 🛠️ MCP Tool Calling System
- AI does not directly modify data
- Uses tools via MCP server
- Ensures safe and modular execution

## 📊 Progress Tracking
- Tracks daily student activity
- Assigns marks for completed tasks
- Stores progress history in PostgreSQL

## 📲 Telegram Bot Interface
- Simple chat-based learning system
- Sends daily tasks to students
- Collects responses and updates progress

## 🧠 AI Tutor
- Explains concepts using Groq LLM
- Provides personalized learning support
- Acts as interactive academic assistant

---

# 🔄 Workflow

1. Student starts chat in Telegram
2. Bot receives request (bot.py)
3. AI generates plan or response (ai_tutor.py)
4. If tool required → MCP server is triggered
5. Tool executed from mcp_tools.py
6. services.py processes logic
7. PostgreSQL stores or fetches data
8. Response sent back to student

---

# 🔐 Environment Variables

DB_HOST=localhost  
DB_PORT=5432  
DB_NAME=your_database  
DB_USER=your_username  
DB_PASSWORD=your_password  

GROQ_API_KEY=your_groq_api_key  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token  

---

# ▶️ How to Run

## Install dependencies
pip install -r req.txt

## Start MCP Server
uvicorn mcp_server:app --reload

## Run Telegram Bot
python bot.py

---

# 🚀 Future Improvements

- Add vector memory (FAISS / ChromaDB)
- Add admin dashboard for teachers
- Dockerize full system
- Deploy on cloud (AWS / Render / Railway)
- Add multi-agent AI system (planner + tutor + evaluator)
- Add analytics dashboard for student performance

---

## 👨‍💻 Author

**Madhivanan**  
AI/ML Enthusiast | Backend Developer

**Specializations:**
- AI Agent Systems
- Education Automation Platforms
- LLM Tool-Based Architectures

# 📌 Summary

This project is an AI-driven education system that transforms static syllabus into a **dynamic, structured, and trackable learning experience** using modern AI architecture (LLM + Tools + Backend + Database).