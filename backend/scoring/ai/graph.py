from langgraph.graph import StateGraph, START, END
from .schema import SecurityAgentState, SalaryAgentState, EmployerDomainExtractionState
from .nodes import suspicious_nodes, suspicious_salary_nodes, employer_host_extraction_nodes

"""Employer Host Extraction Nodes"""
employer_host_extraction_requests = StateGraph(EmployerDomainExtractionState)
employer_host_extraction_requests.add_node("employer_host_extraction_requests", employer_host_extraction_nodes)

employer_host_extraction_requests.add_edge(START, "employer_host_extraction_requests")
employer_host_extraction_requests.add_edge("employer_host_extraction_requests", END)

employer_host_extraction_graph = employer_host_extraction_requests.compile()
"""Check Suspicious Nodes"""
check_suspicious_requests = StateGraph(SecurityAgentState)

check_suspicious_requests.add_node('suspicious_nodes', suspicious_nodes)

check_suspicious_requests.add_edge(START, "suspicious_nodes")
check_suspicious_requests.add_edge("suspicious_nodes", END)

fraud_graph = check_suspicious_requests.compile()

"""Check Salary"""
check_salary_requests = StateGraph(SalaryAgentState)
check_salary_requests.add_node("check_salary_requests", suspicious_salary_nodes)

check_salary_requests.add_edge(START, "check_salary_requests")
check_salary_requests.add_edge("check_salary_requests", END)

salary_graph = check_salary_requests.compile()