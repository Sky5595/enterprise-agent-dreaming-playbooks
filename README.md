# Enterprise Agent Dreaming Playbooks

> **A hands-on evaluation and reference implementation of Anthropic's "Dreaming" concept for Claude Managed Agents**, announced at Code with Claude on May 5, 2026.

This project is a minimal, self-contained implementation inspired by Anthropic's official *dreaming* feature — a scheduled process that reviews past agent sessions, extracts failure patterns, and helps agents self-improve over time. Rather than using the managed platform API directly, this repo builds the same loop from first principles so engineers can understand, extend, and adapt it to any LLM provider or enterprise context.

***

## What Is Anthropic's Dreaming Feature?

On May 5, 2026, Anthropic introduced **dreaming** as a research preview in Claude Managed Agents. As described in Anthropic's official announcement:

> *"Dreaming extends memory by reviewing past sessions to find patterns and help agents self-improve... It surfaces patterns that a single agent can't see on its own, including recurring mistakes, workflows that agents converge on, and preferences shared across a team."*
>
> — [Anthropic Claude Blog, May 5 2026](https://claude.com/blog/new-in-claude-managed-agents)

Crucially, dreaming does **not** modify model weights. It writes learnings as plain-text notes and structured playbooks that future sessions can reference — making the process fully observable, auditable, and human-reviewable.

Early production results from Anthropic's partners have been striking: Harvey (legal AI) reported a **~6× increase in task completion rates**, and Wisedocs (medical document review) cut review time by **50%** after implementing related features.

This project evaluates and operationalizes that same concept for enterprise support agents, with a human-in-the-loop review gate appropriate for regulated industries.

***

## What This Project Does

This is a reference implementation of an **Agent SRE Dreaming Loop** that:

- Collects enterprise agent sessions as structured JSONL
- Exposes a FastAPI endpoint to submit new sessions
- Runs a "dream" pipeline that analyzes **interesting sessions** (escalations, bad feedback) and proposes:
  - **Playbooks** — step-by-step YAML response strategies with detection rules
  - **System prompt updates** — targeted, evidence-based prompt patches
  - **Routing suggestions** — explicit conditions for human handoff
  - **Dream reports** — timestamped audit logs of every dream cycle

Nothing auto-deploys. Every output is written to disk for human review before touching production — a deliberate design choice for compliance-sensitive environments (SOC 2, HIPAA, ISO 27001).

***

## Architecture

```
Agent Runtime → Sessions (JSONL)
                      ↓
         Filter: Escalations + Bad Feedback (≤3/5)
                      ↓
         Cluster by Primary Tag
                      ↓
         LLM Dreamer (Claude / any provider)
                      ↓
  ┌────────────────────────────────────────┐
  │  Playbook YAML │ Prompt Patch │ Routing │
  └────────────────────────────────────────┘
                      ↓
         Human Review → Deploy
```

***

## Project Structure

```
src/
  main.py              # FastAPI app — /sessions and /dream endpoints
  dream.py             # Core dreaming pipeline (filter, cluster, generate)
  llm_client.py        # Anthropic API client (provider-agnostic abstraction)
  models.py            # Pydantic models: Session, AgentAction, PlaybookSuggestion
  config.py            # Environment config (API key, model name, paths)
  collect_sessions.py  # Demo session seeder

data/
  sessions.jsonl       # Append-only session log

playbooks/             # Generated YAML playbooks (one per failure cluster)
prompts/               # Suggested system prompt updates
routing/               # Suggested routing rules
reports/               # Timestamped dream reports
```

***

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env        # Set ANTHROPIC_API_KEY

# Seed demo sessions
python -m src.collect_sessions

# Run API
uvicorn src.main:app --reload

# Submit sessions via POST /sessions
# Then trigger a dream pass
python -m src.dream
# or: POST /dream via the API
```

***

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/sessions` | Submit a new agent session |
| `POST` | `/dream` | Trigger a dream analysis cycle |

***

## Session Schema

```json
{
  "session_id": "demo-001",
  "timestamp": "2026-05-09T00:00:00Z",
  "user_id": "user-1",
  "channel": "support_portal",
  "user_input": "I filed a claim last week and still don't see any update.",
  "agent_actions": [
    {
      "type": "tool_call",
      "tool": "claims_api.get_claim_status",
      "result_summary": "Claim in manual review, ETA 3–5 business days."
    }
  ],
  "agent_output": "Your claim is in manual review. It usually takes 3–5 business days.",
  "outcome": "escalated_to_human",
  "user_feedback": 2,
  "tags": ["claims_status", "delay", "frustration"]
}
```

***

## LLM Provider

The implementation uses **Anthropic Claude (claude-3-5-sonnet)** by default via `llm_client.py`. The abstraction is fully provider-agnostic — swap in any LLM by replacing the `propose_playbook_for_cluster()` function.

***

## Design Decisions & Differences from Anthropic's Platform

| Aspect | Anthropic Managed Agents | This Implementation |
|---|---|---|
| Memory store | Platform-managed vector store | Append-only JSONL |
| Dream trigger | Scheduled (platform-side) | Manual or API-triggered |
| Output | Reorganized memory store | YAML playbooks + MD patches |
| Auto-deploy | Optional (configurable) | Never — always human-reviewed |
| Provider | Claude only | Any LLM (provider-agnostic) |
| Scope | Full managed agent platform | Minimal SRE loop only |

***

## Roadmap

- [ ] Embedding-based clustering (semantic similarity beyond tag matching)
- [ ] A/B testing gates for proposed prompt updates
- [ ] Multi-agent dreamer architecture (specialized dreamers per failure domain)
- [ ] CI/CD integration for approved playbook auto-deploy on merge
- [ ] Support for Anthropic's official Dreams API as an optional backend

***

## References

- [Anthropic Official Announcement — *New in Claude Managed Agents: dreaming, outcomes, and multiagent orchestration*](https://claude.com/blog/new-in-claude-managed-agents) (May 5, 2026)
- [Anthropic Dreams API Docs](https://platform.claude.com/docs/en/managed-agents/dreams)
- [VentureBeat — *Anthropic introduces "dreaming"*](https://venturebeat.com/technology/anthropic-introduces-dreaming-a-system-that-lets-ai-agents-learn-from-their-own-mistakes) (May 7, 2026)

***

## License

MIT
