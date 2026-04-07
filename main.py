import os
from datetime import datetime
from fastapi import FastAPI
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from memory import save_memory, get_memory

from tools import get_tools

load_dotenv()

# ✅ WORKING MODEL
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

tools = get_tools()

# ✅ Inject current time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# ✅ STRICT PROMPT (FIXES RANDOM + MULTI CALL ISSUE)
prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
You are a personal AI assistant.

Current date and time: {current_time}

Rules:
- If user asks to set a reminder → use set_reminder tool
- If user asks to calculate → use calculator
- If user asks to schedule → use schedule_meeting
- Do NOT create multiple reminders
- Perform only what user asks

After using tool, return final answer.
"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# ✅ LIMIT EXECUTION (VERY IMPORTANT)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
)

# FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Personal AI Agent Running 🚀"}

@app.get("/chat")
def chat(q: str):
    try:
        q_lower = q.lower()

        # Get past memory
        past = get_memory()
        memory_context = "\n".join(
            [f"User: {m[0]} → AI: {m[1]}" for m in past]
        )

        # TOOL ROUTING
        if "reminder" in q_lower:
            response = tools[1].invoke(q)

        elif "schedule" in q_lower or "meeting" in q_lower:
            response = tools[2].invoke(q)

        elif any(op in q for op in ["+", "-", "*", "/"]):
            response = tools[0].invoke(q)

        elif "search" in q_lower:
            response = tools[3].invoke(q)

        else:
            # LLM with memory
            prompt = f"""
Previous conversation:
{memory_context}

User: {q}
"""
            result = llm.invoke(prompt)
            response = result.content

        # Save memory
        save_memory(q, response)

        return {"response": response}

    except Exception as e:
        return {"error": str(e)}