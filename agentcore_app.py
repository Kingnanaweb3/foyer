"""Bedrock AgentCore Runtime entry point.

Wraps the existing orchestrator in the HTTP contract AgentCore expects. The
agent logic itself is unchanged -- this file only adapts the interface.

Local test:
  python agentcore_app.py
  curl -X POST http://localhost:8080/invocations \
    -H "Content-Type: application/json" \
    -d '{"prompt":"When is the food drive?"}'

Deploy:
  agentcore configure -e agentcore_app.py
  agentcore launch
"""
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from orchestrator import foyer

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    """AgentCore hands us a JSON payload; we return the agent's reply as text."""
    user_message = payload.get("prompt", "Hello")
    return str(foyer(user_message))


if __name__ == "__main__":
    app.run()
