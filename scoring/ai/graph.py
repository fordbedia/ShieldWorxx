from langgraph.graph import StateGraph, START, END
from .schema import SecurityAgentState
from .nodes import suspicious_nodes

workflow = StateGraph(SecurityAgentState)

workflow.add_node('start')
workflow.add_node('suspicious_nodes', suspicious_nodes)
workflow.add_node('end')

graph = workflow.compile()