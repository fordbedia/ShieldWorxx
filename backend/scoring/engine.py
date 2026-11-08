from .checks import check_domain_age, check_recruiter_email
from .scorer import score
from .fetchers import fetch_text
from .checks import check_employer_host, check_suspicious_requests, check_salary, check_suspicious_tld, check_ssl_validity
from .posting import PostDetails, EmployerJobPost

CHECKS_PHASE_1 = [
    check_domain_age,
    check_recruiter_email
]
CHECKS_PHASE_2 = [
    check_suspicious_requests, # AI
    check_salary, # AI
    check_suspicious_tld,
    check_ssl_validity,
]

def run_all_checks(posting):
    if not posting.text:
        posting.text = fetch_text(posting.url) or ""

    if not posting.employer_job:
        employer_job_post = check_employer_host(posting)
        employer_host = employer_job_post["employer_host"]
        posting.employer_job = EmployerJobPost(
            company=employer_job_post["company_name"],
            host=employer_host["host"] if employer_host else None,
        )
    basic_findings = [check(posting) for check in CHECKS_PHASE_1]
    # find and extract emails
    recruiter_email_data = {item['name']: item['details'] for item in basic_findings if 'details' in item}
    domain = {"domain": item['domain'] for item in basic_findings if 'domain' in item}
    if recruiter_email_data['recruiter_email'] is not None and recruiter_email_data['recruiter_email']['company']:
        posting.post_details = PostDetails(emails=recruiter_email_data['recruiter_email']['company'], domain=domain['domain'])
    advance_findings = [check(posting) for check in CHECKS_PHASE_2]
    return basic_findings, advance_findings, score(basic_findings + advance_findings)