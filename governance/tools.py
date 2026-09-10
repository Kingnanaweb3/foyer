"""
Shared trust layer used by every sub-agent.
- log_decision: plain-language audit trail a non-technical board member can read.
- queue_approval: anything donor-facing or reputational waits here for a human tap
  instead of sending automatically.
"""
from datetime import datetime, timezone
from strands import tool
from tools.store import load, save

@tool
def log_decision(agent_name: str, action: str, reason: str) -> str:
    """
    Record why an agent took an action, in plain language.

    Args:
        agent_name: which sub-agent acted (e.g. "front_desk", "donor_steward")
        action: what it did (e.g. "confirmed RSVP")
        reason: why, in plain language a non-technical person can read
    """
    log = load("decision_log.json")
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "action": action,
        "reason": reason,
    }
    log.append(entry)
    save("decision_log.json", log)
    return f"Logged: {action}"

@tool
def queue_approval(agent_name: str, action_type: str, content: str, reason: str) -> str:
    """
    Put a risky or donor-facing action in the human approval queue instead of
    sending it directly. Use this for anything money-adjacent or reputational.

    Args:
        agent_name: which sub-agent is requesting approval
        action_type: e.g. "donor_message", "refund"
        content: the actual draft (e.g. the message text) waiting for approval
        reason: plain-language explanation of why this action is being proposed
    """
    queue = load("approval_queue.json")
    entry = {
        "id": f"appr_{len(queue) + 1}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "action_type": action_type,
        "content": content,
        "reason": reason,
        "status": "pending",
    }
    queue.append(entry)
    save("approval_queue.json", queue)
    return f"Queued for human approval (id: {entry['id']}). It will not send until approved."
