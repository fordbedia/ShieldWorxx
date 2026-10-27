from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Literal,TypedDict

class VerdictState(BaseModel):        # what the AI must return
    verdict: Literal["safe", "suspicious"]
    penalty: Literal[0, -10, -20, -30, -40]
    reason: str

class SecurityAgentState(TypedDict):
    verdict: Literal["safe", "suspicious"]
    penalty: Literal[0, -10, -20, -30, -40]
    reason: str
    text: str