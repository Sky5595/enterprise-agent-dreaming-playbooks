from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import os

from .config import DATA_DIR, SESSIONS_FILE
from .models import Session
from .dream import run_dream

app = FastAPI(title="Enterprise Agent Dreaming Playbooks")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(DATA_DIR, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


@app.post("/sessions")
async def add_session(session: Session):
    # append to JSONL
    line = session.model_dump()
    with open(SESSIONS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(line) + "
")
    return {"status": "stored", "session_id": session.session_id}


@app.post("/dream")
async def trigger_dream():
    run_dream()
    return {"status": "dream_started"}
