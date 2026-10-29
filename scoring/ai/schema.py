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

class SalaryExtraction(BaseModel):
    found: bool
    min: float | None
    max: float | None
    period: Literal["hour", "week", "month", "year"] | None
    quotes: list[str]   # the EXACT text spans the numbers came from

class PaySignal(BaseModel):
    detected: bool
    quotes: list[str]
    reason: str

class SalaryAnalysis(BaseModel):
    extraction: SalaryExtraction
    vague_pay: PaySignal
    commission_only: PaySignal
    too_good_to_be_true: PaySignal