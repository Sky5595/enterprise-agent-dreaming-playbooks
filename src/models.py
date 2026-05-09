from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any


class AgentAction(BaseModel):
    type: str
    tool: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    result_summary: Optional[str] = None


class Session(BaseModel):
    session_id: str
    timestamp: str
    user_id: str
    channel: str
    user_input: str
    agent_actions: List[AgentAction] = Field(default_factory=list)
    agent_output: str
    outcome: Literal["success", "escalated_to_human", "user_dissatisfied"]
    user_feedback: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class PlaybookSuggestion(BaseModel):
    cluster_name: str
    pattern_summary: str
    playbook_yaml: str
    prompt_updates: List[str]
    routing_suggestions: List[str]
