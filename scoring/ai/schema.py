from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Literal

class Verdict(BaseModel):        # what the AI must return
    verdict: Literal["safe", "suspicious"]
    flags: list[str]
    evidence: list[str]

class ReviewState(BaseModel):    # what flows between nodes
    text: str
    rule_matches: list[str]
    question: str
    result: Verdict | None

class SecurityAgentState(BaseModel):
    text: str
    rule_matches: list[str]
    result: Verdict | None