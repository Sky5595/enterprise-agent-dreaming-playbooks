import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-3-5-sonnet-latest")

DATA_DIR = "data"
SESSIONS_FILE = os.path.join(DATA_DIR, "sessions.jsonl")
PLAYBOOKS_DIR = "playbooks"
PROMPTS_DIR = "prompts"
ROUTING_DIR = "routing"
REPORTS_DIR = "reports"
