"""
Human-side operations on the approval queue and decision log.

These are plain Python functions (not @tool) on purpose: they are actions the
HUMAN takes, not actions the agent is allowed to take. Keeping them out of the
tool registry is what makes the boundary real -- no prompt can talk the agent
into approving its own draft.
"""
from datetime import datetime, timezone
from tools.store import load, save


def list_pending():
    """Every queued action still waiting on a human decision."""
    return [item for item in load("approval_queue.json") if item["status"] == "pending"]


def list_all():
    """Full queue, newest first -- pending, approved and rejected."""
    return list(reversed(load("approval_queue.json")))


def decide(approval_id: str, decision: str, note: str = ""):
    """
    Approve or reject one queued action.

    decision: "approved" or "rejected"
    Returns the updated entry, or None if the id wasn't found.
    """
    queue = load("approval_queue.json")
    target = next((i for i in queue if i["id"] == approval_id), None)
    if target is None:
        return None

    target["status"] = decision
    target["decided_at"] = datetime.now(timezone.utc).isoformat()
    target["note"] = note
    save("approval_queue.json", queue)

    # Mirror the human's decision into the same audit trail the agent writes to,
    # so the log tells one continuous story rather than two partial ones.
    log = load("decision_log.json")
    log.append({
        "timestamp": target["decided_at"],
        "agent": "human_admin",
        "action": f"{decision} {target['action_type']} ({approval_id})",
        "reason": note or f"Reviewed by a human and {decision}.",
    })
    save("decision_log.json", log)
    return target


def read_log(limit: int = 50):
    """Most recent decision-log entries, newest first."""
    return list(reversed(load("decision_log.json")))[:limit]
