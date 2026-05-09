import json
import os
from collections import defaultdict
from datetime import datetime
from typing import List

from .config import (
    SESSIONS_FILE,
    PLAYBOOKS_DIR,
    PROMPTS_DIR,
    ROUTING_DIR,
    REPORTS_DIR,
)
from .models import Session
from .llm_client import propose_playbook_for_cluster


def load_sessions() -> List[Session]:
    sessions: List[Session] = []
    if not os.path.exists(SESSIONS_FILE):
        return sessions
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            sessions.append(Session(**data))
    return sessions


def filter_interesting(sessions: List[Session]) -> List[Session]:
    return [
        s
        for s in sessions
        if s.outcome in {"escalated_to_human", "user_dissatisfied"}
        or (s.user_feedback is not None and s.user_feedback <= 3)
    ]


def group_by_primary_tag(sessions: List[Session]):
    clusters = defaultdict(list)
    for s in sessions:
        key = s.tags[0] if s.tags else "misc"
        clusters[key].append(s)
    return clusters


def ensure_dirs():
    for d in [PLAYBOOKS_DIR, PROMPTS_DIR, ROUTING_DIR, REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)


def run_dream():
    ensure_dirs()
    all_sessions = load_sessions()
    interesting = filter_interesting(all_sessions)
    clusters = group_by_primary_tag(interesting)

    if not interesting:
        print("No interesting sessions found. Nothing to dream about.")
        return

    playbook_files = []
    prompt_updates_all = []
    routing_all = []

    for tag, sessions in clusters.items():
        suggestion = propose_playbook_for_cluster(tag, sessions)

        # Write playbook yaml
        pb_path = os.path.join(PLAYBOOKS_DIR, f"{tag}.yaml")
        with open(pb_path, "w", encoding="utf-8") as f:
            f.write(suggestion.playbook_yaml)
        playbook_files.append(pb_path)

        # Append prompt updates
        if suggestion.prompt_updates:
            prompt_updates_all.append(f"## Cluster: {tag}
")
            for u in suggestion.prompt_updates:
                prompt_updates_all.append(f"- {u}
")

        # Append routing suggestions
        if suggestion.routing_suggestions:
            routing_all.append(f"# Cluster: {tag}
")
            for r in suggestion.routing_suggestions:
                routing_all.append(f"- {r}
")

    # Write prompt updates file (append mode)
    if prompt_updates_all:
        with open(os.path.join(PROMPTS_DIR, "suggested_updates.md"), "a", encoding="utf-8") as f:
            f.write("
".join(prompt_updates_all) + "
")

    # Write routing suggestions file (append mode)
    if routing_all:
        with open(os.path.join(ROUTING_DIR, "routing_suggestions.yaml"), "a", encoding="utf-8") as f:
            f.write("
".join(routing_all) + "
")

    # Write report
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    report_path = os.path.join(REPORTS_DIR, f"dream-{ts}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Dream Report {ts}

")
        f.write(f"Total sessions: {len(all_sessions)}\n
")
        f.write(f"Interesting sessions: {len(interesting)}\n
")
        f.write(f"Clusters: {len(clusters)}\n
")
        f.write("## Playbooks written
")
        for p in playbook_files:
            f.write(f"- {p}
")

    print(f"Dream complete. Report written to {report_path}")


if __name__ == "__main__":
    run_dream()
