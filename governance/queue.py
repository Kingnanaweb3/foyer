"""
Human-side operations on the approval queue and decision log.

These are plain Python functions (not @tool) on purpose: they are actions the
HUMAN takes, not actions the agent is allowed to take. Keeping them out of the
tool registry is what makes the boundary real -- no prompt can talk the agent
into approving its own draft.
"""
from datetime import datetime, timezone

from governance.mailer import send_donor_message
from tools.store import load, save


def _recipient_for(draft: str):
    """Work out who an approved draft is addressed to.

    The queue entry carries the message but not the address -- queue_approval
    is a tool the agent calls, and widening its signature would mean changing
    what the agent is asked to produce. Matching the draft's greeting against
    the donor list keeps all of this on the human side of the boundary.
    """
    for donor in load("donors.json"):
        first = donor["name"].split()[0]
        if f"Hi {first}" in draft:
            return donor
    return None


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

    # Only a pending item can be decided. Without this a double click
    # re-approves and sends the donor a second copy of the same message.
    if target["status"] != "pending":
        return target

    target["status"] = decision
    target["decided_at"] = datetime.now(timezone.utc).isoformat()
    target["note"] = note

    # Only an approval sends, and only from here -- the agent has no path to
    # this function. A provider failure is recorded, never raised: a human's
    # decision does not get rolled back because email had a bad minute.
    delivery = None
    if decision == "approved" and target.get("action_type") == "donor_message":
        donor = _recipient_for(target["content"])
        if donor:
            sent, detail = send_donor_message(
                to=donor["email"],
                subject=f"A note from Riverside Community Trust",
                body=target["content"],
            )
            target["delivered"] = sent
            target["delivery_detail"] = detail
            delivery = (donor["name"], sent, detail)

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
    # The send is its own line in the trail. If it failed, that is on the
    # record too -- a log that only shows successes is not an audit trail.
    if delivery:
        name, sent, detail = delivery
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": "system",
            "action": f"sent message to {name}" if sent
                      else f"delivery failed for {name}",
            "reason": detail,
        })

    save("decision_log.json", log)
    return target


def read_log(limit: int = 50):
    """Most recent decision-log entries, newest first."""
    return list(reversed(load("decision_log.json")))[:limit]
