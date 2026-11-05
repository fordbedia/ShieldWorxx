from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Literal,TypedDict

class VerdictState(BaseModel):        # what the AI must return
    verdict: Literal["safe", "suspicious"]
    penalty: Literal[0, -10, -20, -30, -40]
    evidence: list[str]
    reason: str

class SecurityAgentState(TypedDict):
    verdict: Literal["safe", "suspicious"]
    penalty: Literal[0, -10, -20, -30, -40]
    evidence: list[str]
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
    penalty: Literal[0, -5, -15]

class SalaryAnalysis(BaseModel):
    # Declared first so the model identifies the role before judging pay.
    title: str | None = Field(description="Job title of the advertised position, or null if not stated")
    company: str | None = Field(description="Hiring company name (not the job board), or null if not named")
    extraction: SalaryExtraction
    vague_pay: PaySignal
    commission_only: PaySignal
    too_good_to_be_true: PaySignal
    penalty: Literal[0, -5, -15]
    reason: str

class SalaryAgentState(TypedDict):
    text: str
    salary_analysis: SalaryAnalysis | None