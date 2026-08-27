from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mplads import chat as chatbot, llm

app = FastAPI(title="Thadam AI Assistant API")

class ChatTurn(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: list[ChatTurn] = []
    lang: str = "en"

@app.post("/api/chat")
def chat(req: ChatRequest) -> dict:
    """Ask the assistant with multi-turn history and native language support."""
    if not req.question.strip():
        raise HTTPException(400, "question is required")
    history = [{"role": t.role, "content": t.content} for t in req.history][-12:]
    return chatbot.answer(req.question.strip(), history=history, language=req.lang)

@app.get("/api/chat/capabilities")
def chat_capabilities() -> dict:
    """Returns supported tools, languages, and starter prompt categories."""
    return {
        "live": llm.available(),
        "languages": llm.LANGUAGES,
        "tools": [
            {"name": name, "does": (fn.__doc__ or "").strip().splitlines()[0]}
            for name, fn in chatbot.TOOL_FUNCS.items()
        ],
        "categories": [
            {
                "category": "Portfolio & Scale",
                "icon": "📊",
                "prompts": [
                    "How many works and leads are in the national portfolio?",
                    "What does exposure at risk mean?",
                    "What is the Portfolio Health Index?",
                ],
            },
            {
                "category": "High-Risk Leads",
                "icon": "🚨",
                "prompts": [
                    "Show me the top prioritized investigation leads",
                    "Tell me about MP3018356-W86316 in Saran",
                ],
            },
            {
                "category": "State & Agency Audit",
                "icon": "🏛️",
                "prompts": [
                    "Compare Bihar and Uttar Pradesh",
                    "Which state has the highest exposure at risk?",
                    "Tell me about District Planning Officer, Saran",
                ],
            },
            {
                "category": "7 Intelligence Engines",
                "icon": "🤖",
                "prompts": [
                    "What are the 7 intelligence engines?",
                    "Explain the Cox proportional hazards completion risk",
                    "What is the Audit-ROI ranking formula?",
                ],
            },
        ],
    }
