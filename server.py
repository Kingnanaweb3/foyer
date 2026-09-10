"""
Foyer web server.

Serves two surfaces from one process:
  /            -> community chat (what a neighbour or donor sees)
  /admin       -> approval queue + decision log (what the nonprofit admin sees)

FOYER_DEMO_MODE=1 runs the UI against canned responses instead of calling
Bedrock. It exists so frontend work isn't blocked on model access -- do NOT
record the submission demo in this mode.
"""
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from governance.queue import list_all, list_pending, decide, read_log

DEMO_MODE = os.getenv("FOYER_DEMO_MODE") == "1"

app = FastAPI(title="Foyer")


class ChatIn(BaseModel):
    message: str


class DecisionIn(BaseModel):
    note: str = ""


@app.post("/api/chat")
def chat(body: ChatIn):
    """Route an inbound message through the Foyer orchestrator."""
    if DEMO_MODE:
        return {"reply": _canned(body.message), "demo_mode": True}

    # Imported lazily so the server still boots (and /admin still works) when
    # Bedrock credentials aren't available yet.
    from orchestrator import foyer
    return {"reply": str(foyer(body.message)), "demo_mode": False}


@app.get("/api/approvals")
def approvals():
    return {"pending": list_pending(), "all": list_all()}


@app.post("/api/approvals/{approval_id}/{decision}")
def approval_decision(approval_id: str, decision: str, body: DecisionIn):
    if decision not in {"approved", "rejected"}:
        return {"error": "decision must be 'approved' or 'rejected'"}
    result = decide(approval_id, decision, body.note)
    if result is None:
        return {"error": f"no approval found with id {approval_id}"}
    return {"updated": result}


@app.get("/api/log")
def log():
    return {"entries": read_log()}


def _canned(message: str) -> str:
    """Offline stand-in so the UI can be built and styled without Bedrock."""
    lowered = message.lower()
    if "park" in lowered or "food drive" in lowered or "when" in lowered:
        return ("Fall Food Drive - September 20 at the Community Center, "
                "123 Main St. Parking is free in the lot behind the building. "
                "18 of 50 spots are still open.")
    if "rsvp" in lowered or "sign up" in lowered or "register" in lowered:
        return "You're registered for the Fall Food Drive on September 20. See you there!"
    if "lapsing" in lowered or "donor" in lowered:
        return ("James Okafor is lapsing - last gift 192 days ago against a usual "
                "45-day gap. I've drafted a re-engagement note and queued it for "
                "your approval. It won't send until you approve it.")
    return "I can help with event details, RSVPs, and donor questions. What do you need?"


app.mount("/", StaticFiles(directory="web", html=True), name="web")
