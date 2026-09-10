"""Single source of truth for which Bedrock model every agent uses.

Strands defaults to a `global.` cross-region inference profile, which many
accounts can't invoke. Pinning to a regional profile here means one edit
changes all three agents.

To see what your account can actually call:
  aws bedrock list-inference-profiles --region us-east-1 \
    --query "inferenceProfileSummaries[?contains(inferenceProfileId,'claude')].inferenceProfileId" \
    --output table
"""
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
