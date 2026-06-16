# 💰 Personalized Financial Advisory Chatbot

An AI-powered chatbot that delivers **personalized financial advice** by combining Retrieval-Augmented Generation (RAG) with user profile context. Built end-to-end — from document ingestion to a deployed, shareable web app.

🔗 **Live Demo:** https://financial-advisor-chatbot-nnpbvqet3kdvoafryqmt65.streamlit.app/

---

## 🎯 What It Does

Ask any financial question — "Should I invest in SIP or FD?", "How much should I save for my goals?" — and get advice that's tailored to **your** age, income, savings, risk appetite, and investment goal, grounded in official RBI financial literacy documents.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | OpenAI (gpt-3.5-turbo) |
| Embeddings | OpenAI (text-embedding-3-small) |
| Vector Store | FAISS |
| Agent Orchestration | LangGraph |
| Data Validation | Pydantic |
| Frontend | Streamlit |
| Document Loading | LangChain (PyPDFLoader) |

---

## 🏗️ Architecture
User Input (Profile + Question)
│
▼
LangGraph Agent
│
┌────┴────┐

│ Retrieve │ → searches FAISS vectorstore (RBI documents)

└────┬────┘
│
┌────┴────┐

│ Respond  │ → combines profile + retrieved docs → OpenAI LLM

└────┬────┘
│
▼
Personalized Answer
---

**Data Flow:**
1. RBI financial literacy PDFs are loaded, chunked, and embedded into a FAISS vector store (one-time ingestion)
2. User fills in their profile (age, income, expenses, risk appetite, goal) via the Streamlit sidebar
3. User asks a question in natural language
4. The **Retrieve node** searches the vectorstore for the top relevant chunks
5. The **Respond node** combines the user's profile, retrieved context, and question, then queries the LLM
6. A personalized, actionable answer is returned and displayed in the chat
---

## 📁 Project Structure
financial-advisor-chatbot/

├── data/finance_docs/      # RBI financial literacy PDFs
├── src/
│   ├── ingest.ipynb        # PDF loading, chunking, embedding
│   ├── agent.ipynb         # LangGraph agent (retrieve + respond nodes)
│   ├── profile.ipynb       # Pydantic user profile model
│   └── vectorstore/        # Saved FAISS index
├── app.py                  # Streamlit application
├── requirements.txt
└── README.md

---

## 📚 Data Sources

Official RBI financial literacy publications:
- FAME Booklet (2024) — budgeting, banking, borrowing
- RBI Financial Literacy Guide — banking concepts in depth
- RBI School Financial Literacy Guide — savings, SIP, investment basics

---

## ✨ Key Features

- **Personalization** — advice adapts to user's financial profile, not generic responses
- **Grounded answers** — retrieval from verified RBI documents reduces hallucination
- **Conversational memory** — maintains context across the chat session
- **Clean, modular architecture** — separate ingestion, agent, and UI layers

---

## 🚀 Run Locally

```bash
git clone https://github.com/Maria-1107/financial-advisor-chatbot.git
cd financial-advisor-chatbot
pip install -r requirements.txt
```

Create a `.env` file:
OPENAI_API_KEY=your_api_key_here

Run the app:
```bash
streamlit run app.py
```

---

## 🔮 Future Improvements

- Add support for multiple document sources (SEBI, AMFI guides)
- Conversation history persistence across sessions
- Multi-agent setup with a dedicated calculation/planning agent
