"""Donor Steward: tracks giving, drafts messages, flags lapsing donors.
Every donor-facing draft must go through queue_approval — this agent never
sends anything directly."""
from strands import Agent
from config import MODEL
from tools.donor_tools import get_donor_profile, check_lapsing_donors, draft_followup_message
from governance.tools import log_decision, queue_approval

donor_steward_agent = Agent(
    name="donor_steward",
    model=MODEL,
    system_prompt=(
        "You manage donor relationships for a small nonprofit. You can look up "
        "donor history and check for lapsing donors freely. If you draft a "
        "thank-you or re-engagement message, you must NEVER send it directly — "
        "always call queue_approval with the draft and your reasoning, so a "
        "human approves it first. Always call log_decision after any action."
    ),
    tools=[get_donor_profile, check_lapsing_donors, draft_followup_message, queue_approval, log_decision],
    callback_handler=None,
)
