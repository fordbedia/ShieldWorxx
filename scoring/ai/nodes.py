from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from .prompts import SYSTEM_PROMPT, USER_TEMPLATE
from .schema import ReviewState

def get_llm():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    # later: return ChatAnthropic(model="...", temperature=0)
    return llm

matches = []
posting = {}
def suspicious_nodes(state: ReviewState):
    question = state['question']
    content = USER_TEMPLATE.format(text=question)
    result = get_llm().invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=content),
    ])
    return result