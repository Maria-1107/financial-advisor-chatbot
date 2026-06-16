import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from typing import TypedDict, List, Optional
from pydantic import BaseModel, computed_field

# ─────────────────────────────────────────
# 1. LOAD ENVIRONMENT + MODELS
# ─────────────────────────────────────────
import os

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv()

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-3.5-turbo")

vectorstore = FAISS.load_local(
    "src/vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

# ─────────────────────────────────────────
# 2. AGENT STATE
# ─────────────────────────────────────────
class AgentState(TypedDict):
    messages: List
    retrieved_docs: str

# ─────────────────────────────────────────
# 3. USER PROFILE
# ─────────────────────────────────────────
class UserProfile(BaseModel):
    name: str
    age: int
    monthly_income: float
    monthly_expense: float
    risk_appetite: str
    investment_goal: str
    existing_investment: Optional[str] = None

    @computed_field
    @property
    def monthly_savings(self) -> float:
        return self.monthly_income - self.monthly_expense

# ─────────────────────────────────────────
# 4. NODES
# ─────────────────────────────────────────
def retrieve_node(state: AgentState):
    # Get last user message
    query = state["messages"][-1].content

    # Search vectorstore for top 3 relevant chunks
    results = vectorstore.similarity_search(query, k=3)

    # Join chunks into one string
    retrieved_docs = "\n\n".join([doc.page_content for doc in results])

    return {"retrieved_docs": retrieved_docs}


def respond_node(state: AgentState):
    # Get conversation history
    messages = state["messages"]

    # Get retrieved chunks
    retrieved_docs = state["retrieved_docs"]

    # Create system prompt
    system_prompt = [
        SystemMessage(content=f"""
        You are a personal financial advisor for Indian users.
        Use the following information to answer the question:
        {retrieved_docs}
        Give specific, simple, actionable advice.
        """)
    ]

    # Send to OpenAI
    response = llm.invoke(system_prompt + messages)

    return {"messages": messages + [AIMessage(content=response.content)]}

# ─────────────────────────────────────────
# 5. BUILD GRAPH
# ─────────────────────────────────────────
graph = StateGraph(AgentState)

graph.add_node("retrieve", retrieve_node)
graph.add_node("respond", respond_node)

graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "respond")
graph.add_edge("respond", END)

agent = graph.compile()

# ─────────────────────────────────────────
# 6. STREAMLIT UI
# ─────────────────────────────────────────
st.title("💰 Personal Financial Advisor")
st.subheader("Your AI-powered financial guide")

# Sidebar — User Profile
with st.sidebar:
    st.header("👤 Your Profile")
    name = st.text_input("Name", value="Rex")
    age = st.slider("Age", 18, 60, 23)
    income = st.number_input("Monthly Income (₹)", value=50000)
    expenses = st.number_input("Monthly Expenses (₹)", value=30000)
    risk = st.selectbox("Risk Appetite", ["low", "medium", "high"])
    goal = st.selectbox("Investment Goal", [
        "retirement", "house", "education", "wealth"
    ])
    existing = st.text_input("Existing Investments (optional)", value="")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about your finances..."):

    # Show user message
    st.chat_message("user").write(prompt)

    # Build user profile
    user = UserProfile(
        name=name,
        age=age,
        monthly_income=income,
        monthly_expense=expenses,
        risk_appetite=risk,
        investment_goal=goal,
        existing_investment=existing if existing else None
    )

    # Run agent
    result = agent.invoke({
        "messages": [HumanMessage(content=f"""
        User Profile:
        - Name: {user.name}
        - Age: {user.age}
        - Monthly Savings: ₹{user.monthly_savings}
        - Risk Appetite: {user.risk_appetite}
        - Goal: {user.investment_goal}
        - Existing Investments: {user.existing_investment}

        Question: {prompt}
        """)],
        "retrieved_docs": ""
    })

    # Get response
    response = result["messages"][-1].content

    # Show response
    st.chat_message("assistant").write(response)

    # Save to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": response})