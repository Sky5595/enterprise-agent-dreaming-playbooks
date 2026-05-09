from typing import List
import anthropic
from .config import ANTHROPIC_API_KEY, MODEL_NAME
from .models import Session, PlaybookSuggestion

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def propose_playbook_for_cluster(cluster_name: str, sessions: List[Session]) -> PlaybookSuggestion:
    """Call Anthropic (or any drop-in LLM) to propose playbook + updates."""
    if client is None:
        # Fallback stub for environments without API key
        return PlaybookSuggestion(
            cluster_name=cluster_name,
            pattern_summary=f"Stub summary for {cluster_name}",
            playbook_yaml=f"name: {cluster_name}
steps:
  - Example step",
            prompt_updates=["Example prompt update"],
            routing_suggestions=["Example routing suggestion"],
        )

    sessions_text = "

".join(
        [
            f"Session {s.session_id}:
User: {s.user_input}
Agent: {s.agent_output}
Outcome: {s.outcome}
Tags: {', '.join(s.tags)}"
            for s in sessions
        ]
    )

    prompt = f"""You are an Agent SRE "Dreamer" for an enterprise support agent.
You review past agent sessions and propose concrete improvements.

Here is a cluster of sessions that had problems (escalations or bad feedback):

{sessions_text}

1. Briefly describe the common pattern in these sessions.
2. Propose a YAML playbook for how the agent should handle this pattern. The YAML keys should be:
   name, description, detection_rules, steps, example_response.
3. Suggest 1-3 updates to the base system prompt as bullet points.
4. Suggest 1-3 routing rules (conditions when this should go to a human).

Return your answer as JSON with keys: pattern_summary, playbook_yaml, prompt_updates, routing_suggestions.
"""

    msg = client.messages.create(
        model=MODEL_NAME,
        max_tokens=800,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )

    # Anthropics responses are structured; simplest is to read first text block
    import json

    content_blocks = msg.content or []
    text = "".join(block.text for block in content_blocks if hasattr(block, "text"))
    try:
        data = json.loads(text)
    except Exception:
        # Very defensive: wrap raw text into structure
        data = {
            "pattern_summary": text[:200],
            "playbook_yaml": "name: TODO
steps: []",
            "prompt_updates": [],
            "routing_suggestions": [],
        }

    return PlaybookSuggestion(
        cluster_name=cluster_name,
        pattern_summary=data.get("pattern_summary", ""),
        playbook_yaml=data.get("playbook_yaml", ""),
        prompt_updates=data.get("prompt_updates", []),
        routing_suggestions=data.get("routing_suggestions", []),
    )
