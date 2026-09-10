"""
Top-level router. Wraps each sub-agent as a callable tool ("agents as tools"
pattern) so the orchestrator can decide which specialist should handle an
incoming message.
"""
from strands import Agent, tool
from config import MODEL_ID
from agents.front_desk import front_desk_agent
from agents.donor_steward import donor_steward_agent

@tool
def ask_front_desk(message: str) -> str:
    """Route a community question or RSVP request to the Front Desk agent."""
    return str(front_desk_agent(message))

@tool
def ask_donor_steward(message: str) -> str:
    """Route a donor-related request to the Donor Steward agent."""
    return str(donor_steward_agent(message))

foyer = Agent(
    name="foyer_orchestrator",
    model=MODEL_ID,
    system_prompt=(
        "You are Foyer, the front door for a small nonprofit with no dedicated "
        "coordinator. Route community/event questions to ask_front_desk, and "
        "donor-related requests to ask_donor_steward. Don't try to answer either "
        "kind of question yourself — always delegate."
    ),
    tools=[ask_front_desk, ask_donor_steward],
)
