from langgraph.graph import StateGraph, START, END
from .schema import SecurityAgentState
from .nodes import suspicious_nodes

workflow = StateGraph(SecurityAgentState)

workflow.add_node('suspicious_nodes', suspicious_nodes)

workflow.add_edge(START, "suspicious_nodes")
workflow.add_edge("suspicious_nodes", END)

graph = workflow.compile()