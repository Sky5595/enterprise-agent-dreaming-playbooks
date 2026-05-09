import json
import os
from datetime import datetime
from .config import DATA_DIR, SESSIONS_FILE

os.makedirs(DATA_DIR, exist_ok=True)


EXAMPLE_SESSIONS = [
    {
        "session_id": "demo-001",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_id": "user-1",
        "channel": "support_portal",
        "user_input": "I filed a claim last week and still don’t see any update.",
        "agent_actions": [
            {
                "type": "tool_call",
                "tool": "claims_api.get_claim_status",
                "arguments": {"claim_id": "CLM-123"},
                "result_summary": "Claim in manual review, ETA 3–5 business days.",
            }
        ],
        "agent_output": "Your claim is in manual review. It usually takes 3–5 business days.",
        "outcome": "escalated_to_human",
        "user_feedback": 2,
        "tags": ["claims_status", "delay", "frustration"],
    },
]


def append_sessions(sessions):
    with open(SESSIONS_FILE, "a", encoding="utf-8") as f:
        for s in sessions:
            f.write(json.dumps(s) + "
")


if __name__ == "__main__":
    append_sessions(EXAMPLE_SESSIONS)
    print(f"Appended {len(EXAMPLE_SESSIONS)} demo sessions to {SESSIONS_FILE}")
