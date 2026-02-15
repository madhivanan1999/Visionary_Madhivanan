import streamlit as st
import faiss
import os
import numpy as np
import pandas as pd
from docx import Document
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from groq import Groq
from dotenv import load_dotenv

# ------------------ LOAD ENV ------------------
load_dotenv()
api_key = os.getenv("Groq_api_key")
Groq_model = Groq(api_key=api_key)

# ------------------ STREAMLIT CONFIG ------------------
st.set_page_config(
    page_title="Madhiverse AI RAG ChatBot",
    layout="wide"
)

# ------------------ DARK VIOLET GLASS UI ------------------
st.markdown("""
<style>

/* ---------- BACKGROUND ---------- */
.stApp {
    background: radial-gradient(circle at top, #1a0833, #0b021a);
    color: #f2ecff;
}

/* ---------- HEADER ---------- */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 20px 24px;
    border-radius: 22px;
    margin-bottom: 20px;
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 10px 40px rgba(128, 0, 255, 0.35);
}

.app-header img {
    width: 48px;
    height: 48px;
}

.app-title {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(90deg, #b98cff, #e0c3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* ---------- FILE UPLOADER ---------- */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 16px;
    border: 1px solid rgba(185, 140, 255, 0.35);
    backdrop-filter: blur(16px);
}

/* ---------- CHAT BUBBLES ---------- */
.stChatMessage {
    border-radius: 22px;
    padding: 16px 20px;
    margin-bottom: 14px;
    backdrop-filter: blur(14px);
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4);
}

/* User */
.stChatMessage[data-testid="chat-message-user"] {
    background: linear-gradient(
        135deg,
        rgba(185, 140, 255, 0.25),
        rgba(120, 60, 255, 0.18)
    );
}

/* Assistant */
.stChatMessage[data-testid="chat-message-assistant"] {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(185, 140, 255, 0.25);
}

/* ---------- CHAT INPUT ---------- */
[data-testid="stChatInput"] textarea {
    background: rgba(255, 255, 255, 0.1);
    color: #f5eeff;
    border-radius: 18px;
    border: 1px solid rgba(185, 140, 255, 0.4);
    padding: 14px;
    font-size: 16px;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #c9baff;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #b98cff;
    box-shadow: 0 0 0 3px rgba(185, 140, 255, 0.35);
}

/* ---------- BUTTONS ---------- */
button {
    background: linear-gradient(135deg, #7a3cff, #b98cff);
    color: white !important;
    border-radius: 18px;
    border: none;
    font-weight: 600;
    padding: 10px 18px;
}

button:hover {
    background: linear-gradient(135deg, #8c4dff, #d1a6ff);
}

/* ---------- MOBILE RESPONSIVE ---------- */
@media (max-width: 768px) {
    .app-title {
        font-size: 22px;
    }

    .app-header {
        padding: 16px;
    }

    .stChatMessage {
        padding: 14px 16px;
    }
}

/* ---------- SCROLLBAR ---------- */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #7a3cff;
    border-radius: 10px;
}

::-webkit-scrollbar-track {
    background: transparent;
}
</style>
""", unsafe_allow_html=True)

# ------------------ BRAND HEADER ------------------
st.markdown("""
<div class="app-header">
    <img src="https://cdn-icons-png.flaticon.com/512/4712/4712109.png">
    <div class="app-title">Madhiverse AI · Conversational RAG</div>
</div>
""", unsafe_allow_html=True)

# ------------------ FILE UPLOAD ------------------
uploaded_file = st.file_uploader(
    "Upload PDF, DOCX, CSV, or Excel",
    type=["pdf", "docx", "csv", "xlsx"]
)

# ------------------ SESSION MEMORY ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None

if "chunks" not in st.session_state:
    st.session_state.chunks = None

# ------------------ FUNCTIONS ------------------
def extract_text(file):
    ext = os.path.splitext(file.name)[1].lower()

    if ext == ".pdf":
        with open("temp.pdf", "wb") as f:
            f.write(file.read())
        loader = PyPDFLoader("temp.pdf")
        pages = loader.load()
        return "\n".join([p.page_content for p in pages])

    elif ext == ".docx":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])

    elif ext == ".csv":
        df = pd.read_csv(file)
        return df.to_string()

    elif ext == ".xlsx":
        df = pd.read_excel(file)
        return df.to_string()

    return ""

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)

@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

def embed_chunks(chunks, model):
    embeddings = model.encode(chunks)
    return np.array(embeddings).astype("float32")

def create_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def retrieve(query, chunks, index, model, k=3):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    _, indices = index.search(query_embedding, k)
    return [chunks[i] for i in indices[0]]

def build_prompt(context_chunks, question):
    context = "\n\n".join(context_chunks)
    return f"""
You are a helpful assistant.
Use previous conversation and the context below.
If answer is not found in context, say "I don't know".

Context:
{context}

Question:
{question}
"""

def ask_groq(messages):
    response = Groq_model.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content

# ------------------ PROCESS DOCUMENT ------------------
if uploaded_file and st.session_state.faiss_index is None:
    with st.spinner("Processing document..."):
        text = extract_text(uploaded_file)
        chunks = chunk_text(text)
        model = load_embedding_model()
        embeddings = embed_chunks(chunks, model)
        index = create_faiss_index(embeddings)

        st.session_state.faiss_index = index
        st.session_state.chunks = chunks

    st.success("Document processed successfully!")

# ------------------ CHAT UI ------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input("Ask something about your document..."):
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    model = load_embedding_model()
    relevant_chunks = retrieve(
        question,
        st.session_state.chunks,
        st.session_state.faiss_index,
        model
    )

    rag_prompt = build_prompt(relevant_chunks, question)

    messages_for_llm = [
        {"role": "system", "content": "You are a conversational RAG assistant."}
    ]
    messages_for_llm.extend(st.session_state.messages)
    messages_for_llm.append(
        {"role": "user", "content": rag_prompt}
    )

    with st.spinner("Thinking..."):
        answer = ask_groq(messages_for_llm)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

    with st.chat_message("assistant"):
        st.markdown(answer)