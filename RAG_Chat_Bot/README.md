# Madhiverse AI – Conversational RAG Chatbot

A **premium, dark-violet, glassmorphic Conversational RAG (Retrieval-Augmented Generation) chatbot** built with **Streamlit**, **FAISS**, **Sentence Transformers**, and **Groq LLMs**.

This app allows users to **upload documents** (PDF, DOCX, CSV, Excel) and **ask natural-language questions** based strictly on the document content.

---

##  Features

- 📄 Upload **PDF, DOCX, CSV, XLSX**
- 🧠 Semantic search using **FAISS vector database**
- 🤖 High-performance LLM via **Groq API**
- 💬 Conversational chat with memory
- 🌙 **Dark Violet UI**
- ✨ **Glassmorphism design**
- 🎨 Branded header (Madhiverse AI)
- 🔒 Secure API key handling via environment variables

---

##  Tech Stack

- **Frontend**: Streamlit
- **Embeddings**: Sentence Transformers
- **Vector DB**: FAISS
- **LLM**: Groq
- **Document Parsing**: PyPDF, python-docx, pandas
- **RAG**: Custom implementation

---

##  Project Structure

```text
madhiverse-rag-chatbot/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
└── .env                # Environment variables (NOT committed)