from fastapi import FastAPI
from pydantic import BaseModel
from rag_engine.retriever import retrieve_context
from rag_engine.generator import generate_answer_local, llm_should_escalate
from rag_engine.tools import send_escalation_email
from prometheus_fastapi_instrumentator import Instrumentator
from rag_engine.db import (
    init_db, save_conversation, get_history_by_user,
    get_total_escalations,
    get_total_escalation_cases,
    get_total_users,
    get_total_questions,
)
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
PROMETHEUS_METRICS_PORT = int(os.getenv("PROMETHEUS_METRICS_PORT", 8001))

app = FastAPI()

#CORS for testing the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("VITE_API_URL")], #Front end url for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#This is for monitoring the tool
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

@app.on_event("startup")
async def startup():
    init_db()

class Query(BaseModel):
    user_id: str = "123"
    question: str

#Main endpoint, to chat with the virtual assistant
@app.post("/chat")
def chat(query: Query):

    #We need to retrieve the most relevant chunks,
    #this function retrieves the 4 most similar chunks
    context = retrieve_context(query.question)

    #this function retrieves the conversation history by user
    #so it can be considered in the prompt for better context
    history = get_history_by_user(query.user_id)
    formatted_history = "\n".join([f"Q: {q}\nA: {a}" for q, a in reversed(history)])
    answer = generate_answer_local(query.question, context, formatted_history)

    #evaluate whether the conversation should be escalated to a human agent
    escalated = llm_should_escalate(query.question, answer)

    if escalated:
        #if escalation is needed then an email will be sent to a human agent
        send_escalation_email(query.user_id, query.question, formatted_history)
        escalated_msg = "Your request has been forwarded to a human agent via email."
        save_conversation(query.user_id, query.question, context, escalated_msg, escalated=True)
        return {"answer": escalated_msg}

    save_conversation(query.user_id, query.question, context, answer, escalated=False)
    return {"answer": answer}

#This endpoint is specific for monitoring escalations
@app.get("/metrics/escalations")
def escalations_metrics():
    total_escalated_users = get_total_escalations()
    total_escalation_cases = get_total_escalation_cases()
    total_users = get_total_users()
    total_questions = get_total_questions()
    rate = round((total_escalation_cases / total_questions) * 100, 2) if total_questions > 0 else 0.0
    return {
        "total_escalated_users": total_escalated_users,
        "total_escalation_cases": total_escalation_cases,
        "total_users": total_users,
        "total_questions": total_questions,
        "escalation_rate_percent": rate
    }
