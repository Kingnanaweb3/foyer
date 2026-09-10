"""Front Desk: answers community questions and handles RSVPs. Low-risk, so it
acts autonomously — no approval gate needed for these actions."""
from strands import Agent
from config import MODEL_ID
from tools.front_desk_tools import get_event_info, make_rsvp
from governance.tools import log_decision

front_desk_agent = Agent(
    name="front_desk",
    model=MODEL_ID,
    system_prompt=(
        "You are the front desk for a small community nonprofit. "
        "Answer questions about events (date, location, parking, spots left) "
        "and handle RSVPs. After any action, call log_decision with a short, "
        "plain-language reason. Keep replies short and friendly."
    ),
    tools=[get_event_info, make_rsvp, log_decision],
)
