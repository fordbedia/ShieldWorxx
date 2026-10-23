from .checks import check_domain_age, check_recruiter_email
from .scorer import score
from .fetchers import fetch_text

CHECKS = [check_domain_age, check_recruiter_email]

def run_all_checks(posting):
    if not posting.text:
        posting.text = fetch_text(posting.url) or ""
    findings = [check(posting) for check in CHECKS]
    return findings, score(findings)