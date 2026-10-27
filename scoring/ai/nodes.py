from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from .prompts import SYSTEM_PROMPT, USER_TEMPLATE
from .schema import VerdictState, SecurityAgentState

def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # later: return ChatAnthropic(model="...", temperature=0)
    return llm

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