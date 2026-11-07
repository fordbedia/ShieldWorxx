from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from .prompts import SYSTEM_PROMPT, USER_TEMPLATE, SALARY_SYSTEM_PROMPT, EMPLOYER_DOMAIN_SYSTEM_PROMPT
from .schema import VerdictState, SecurityAgentState, SalaryAgentState, SalaryAnalysis, EmployerDomainExtractionState, \
    EmployerDomainExtraction

def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # later: return ChatAnthropic(model="...", temperature=0)
    return llm

def employer_host_extraction_nodes(state: EmployerDomainExtractionState):
    employer_host_extraction_llm = get_llm().with_structured_output(EmployerDomainExtraction)
    question = state['text']
    result: EmployerDomainExtraction = employer_host_extraction_llm.invoke([
        SystemMessage(content=EMPLOYER_DOMAIN_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ])

    return {"employer_host": result}

def suspicious_nodes(state: SecurityAgentState):
    """
        The node returns the raw AI reply. get_llm().invoke(...) returns an AIMessage, which is text, not your fields.
        A node must also return a dict of state updates. So
    """
    validate_fraud_llm = get_llm().with_structured_output(VerdictState)
    question = state['text']
    content = USER_TEMPLATE.format(text=question)
    result: VerdictState = validate_fraud_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=content),
    ])
    return result

def suspicious_salary_nodes(state: SalaryAgentState):
    validate_salary_llm = get_llm().with_structured_output(SalaryAnalysis)
    text_prompt = state['text']
    result: SalaryAnalysis = validate_salary_llm.invoke([
        SystemMessage(content=SALARY_SYSTEM_PROMPT),
        HumanMessage(content=text_prompt),
    ])
    return {"salary_analysis": result}
