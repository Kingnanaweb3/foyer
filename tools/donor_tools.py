"""
Tools for the Donor Steward sub-agent.
Anything donor-facing (drafts, messages) does NOT send itself — it must be
queued via governance.tools.queue_approval and approved by a human.
"""
from datetime import datetime, date
from strands import tool
from tools.store import load

@tool
def get_donor_profile(donor_name: str) -> str:
    """
    Get a donor's giving history.

    Args:
        donor_name: name (or partial name) of the donor
    """
    donors = load("donors.json")
    match = next((d for d in donors if donor_name.lower() in d["name"].lower()), None)
    if not match:
        return f"No donor found matching '{donor_name}'."
    return (
        f"{match['name']}: ${match['total_given']} given across {match['gift_count']} gifts. "
        f"Last gift: {match['last_gift_date']}."
    )

@tool
def check_lapsing_donors() -> str:
    """
    Scan all donors and flag anyone overdue based on their normal giving cadence.
    A donor is 'lapsing' if it's been longer than their average gap between gifts,
    plus a 15-day grace window.
    """
    donors = load("donors.json")
    today = date.today()
    at_risk = []

    for d in donors:
        if not d.get("avg_days_between_gifts"):
            continue  # not enough history to judge cadence
        last_gift = datetime.strptime(d["last_gift_date"], "%Y-%m-%d").date()
        days_since = (today - last_gift).days
        threshold = d["avg_days_between_gifts"] + 15
        if days_since > threshold:
            at_risk.append(f"{d['name']} (last gift {days_since} days ago, usual gap {d['avg_days_between_gifts']} days)")

    if not at_risk:
        return "No donors currently lapsing."
    return "Lapsing donors: " + "; ".join(at_risk)

@tool
def draft_followup_message(donor_name: str, message_type: str) -> str:
    """
    Draft a personalized donor message. This does NOT send anything — the draft
    must be queued for human approval separately.

    Args:
        donor_name: name of the donor
        message_type: "thank_you" or "re_engagement"
    """
    donors = load("donors.json")
    match = next((d for d in donors if donor_name.lower() in d["name"].lower()), None)
    if not match:
        return f"No donor found matching '{donor_name}'."

    if message_type == "thank_you":
        draft = (
            f"Hi {match['name'].split()[0]}, thank you again for your recent gift — "
            f"you've now given {match['gift_count']} times, and it genuinely moves our work forward. "
            f"We wouldn't be able to do this without people like you."
        )
    else:  # re_engagement, timed around reciprocity/momentum
        draft = (
            f"Hi {match['name'].split()[0]}, it's been a little while since we last heard from you. "
            f"Your past support (${match['total_given']} over {match['gift_count']} gifts) has made a real "
            f"difference — we'd love to share a quick update on what that's helped us do."
        )
    return draft
