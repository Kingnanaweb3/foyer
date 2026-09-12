"""Tools for the Front Desk sub-agent: event info + RSVPs. Both are low-risk,
so they act directly without needing human approval."""
from strands import tool
from tools.store import load, save

@tool
def get_event_info(event_name: str) -> str:
    """
    Look up date, time, location, parking, and remaining spots for an event.

    Args:
        event_name: name (or partial name) of the event, e.g. "food drive"
    """
    events = load("events.json")
    match = next((e for e in events if event_name.lower() in e["name"].lower()), None)
    if not match:
        return f"No event found matching '{event_name}'."
    spots_left = match["capacity"] - match["spots_taken"]
    return (
        f"{match['name']} — {match['date']}, {match['time']}, "
        f"at {match['location']}. "
        f"Parking: {match['parking']}. Spots left: {spots_left}/{match['capacity']}."
    )

@tool
def make_rsvp(event_name: str, attendee_name: str, attendee_email: str) -> str:
    """
    Reserve a spot for someone at an event, if capacity allows.

    Args:
        event_name: name (or partial name) of the event
        attendee_name: who is RSVPing
        attendee_email: their email, for confirmation
    """
    events = load("events.json")
    match = next((e for e in events if event_name.lower() in e["name"].lower()), None)
    if not match:
        return f"No event found matching '{event_name}'."
    if match["spots_taken"] >= match["capacity"]:
        return f"{match['name']} is full. I can't add {attendee_name} — want me to note them for a waitlist?"

    match["spots_taken"] += 1
    save("events.json", events)

    rsvps = load("rsvps.json")
    rsvps.append({"event": match["name"], "name": attendee_name, "email": attendee_email})
    save("rsvps.json", rsvps)

    return f"Confirmed: {attendee_name} is registered for {match['name']} on {match['date']}."
