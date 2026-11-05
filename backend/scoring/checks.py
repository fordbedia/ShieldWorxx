from .domains import get_registered_domain, get_hostname, get_domain_tld, get_domain_or_subdomain
from .rdap import get_domain_age_days
import re
from .ai.graph import fraud_graph, salary_graph
import tldextract
from .rules import FREE_EMAIL_PROVIDERS, SUSPICIOUS_TLDS, PENALTIES
from .findings import make_finding
import ssl, socket
from datetime import datetime, timezone
from .helpers import check_ssl_status


def check_domain_age(posting) -> dict:
    """Turns the age into a FINDING the user can read."""
    # TODO: return one of these shapes:
    # unknown: {"name": "domain_age", "penalty": 0,   "reason": "Couldn't check domain age"}
    # < 30:    {"name": "domain_age", "penalty": -35, "reason": f"Domain registered {days} days ago"}
    # < 180:   {"name": "domain_age", "penalty": -20, "reason": ...}
    # else:    {"name": "domain_age", "penalty": 0,   "reason": f"Domain is {days // 365} years old"}
    domain = get_registered_domain(get_hostname(posting.url))
    days = get_domain_age_days(domain)

    if days is None:
        return {"name": "domain_age", "domain": domain, "penalty": 0, "severity": "low", "reason": "Couldn't check domain age"}
    elif days < 30:
        return {"name": "domain_age", "domain": domain, "penalty": -35, "severity": "high", "reason": f"Domain registered {days} days ago"}
    elif days < 180:
        return {"name": "domain_age", "domain": domain, "penalty": -20, "severity": "medium", "reason": f"Domain registered {days} days ago"}
    else:
        return {"name": "domain_age", "domain": domain, "penalty": 0, "severity": "low", "reason": f"Domain is {days // 365} years old"}


def check_recruiter_email(posting):
    emails = [e.rstrip(".") for e in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", posting.text)]
    free = [e for e in emails if e.split("@")[1].lower() in FREE_EMAIL_PROVIDERS]
    company = [e for e in emails if e not in free]
    if not emails:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": 0,
                "reason": "No recruiter email in posting", "severity": "low"}
    elif free and company:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": -15,
                "reason": f"Posting lists a company email ({', '.join(company)}) but also a free address ({', '.join(free)})", "severity": "medium"}
    elif free:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": -20,
                "reason": f"Recruiter uses a free email address ({', '.join(free)})", "severity": "high"}
    else:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": 0,
                "reason": f"Recruiter email uses a company domain ({', '.join(company)})", "severity": "low"}


def check_suspicious_requests(posting):
    state = fraud_graph.invoke({
        "text": posting.text
    })

    state.pop("text", None)
    return make_finding(
        name="suspicious_requests",
        severity="high" if state['verdict'] == 'suspicious' else "low",
        **state,
    )


"""
    Where to look in the posting: anything that holds a domain:
    - the apply URL
    - the company website
    - the recruiter’s contact email (everything after the @)
    - links inside the description text (optional, but scammers often hide the real link there)
    Steps to think through:

    1. Collect every URL and email from those fields.
    2. Extract the domain, then the suffix. Don’t use domain.split('.')[-1]. It breaks on company.co.uk 
    and on subdomains like careers.acme.xyz. Look at the tldextract package; it’s the Python version 
    of a “do this properly” Composer package. For URLs, urllib.parse.urlparse gives you the hostname first.
    3. Normalize: lowercase it and strip the www. prefix. 
    Punycode (xn--...) domains are worth a flag of their own, since they’re a common lookalike trick.
    4. Compare against a list of suspicious TLDs. Starting candidates: .xyz, .top, .click, .icu, .buzz, .cfd, .sbs, .loan, .work, .online, .site. 
    Spamhaus publishes a “most abused TLDs” list you can use as a source.
"""


def check_suspicious_tld(posting):
    if posting.post_details is None:
        return make_finding(
            name="suspicious_tld",
            penalty=0,
            reason="No recruiter email in posting",
            bad_tld_count=0,
            penalty_sum=0,
            evidence=[],
            severity="low"
        )
    emails = posting.post_details.emails
    domains = list(dict.fromkeys([get_domain_tld(domain.split('@')[1]) for domain in emails]))
    findings = []
    # Step 1: Collect all the bad TLDs first and their emails
    for domain in domains:
        if domain in SUSPICIOUS_TLDS:
            findings.append({
                "name": "suspicious_tld",
                "penalty": PENALTIES['suspicious_tld'],
                "reason": f"Contact email uses a high-risk domain ({domain})",
                "domains": domain,
                "evidence": [email for email in emails if get_domain_tld(email.split('@')[1]) == domain],
            })
        else:
            findings.append({
                "name": "suspicious_tld",
                "penalty": 0,
                "reason": f"Contact email uses a safe domain ({domain})",
                "domains": domain,
                "evidence": [email for email in emails if get_domain_tld(email.split('@')[1]) == domain],
            })
    # Step 2: Sum up the penalties for bad TLDs and combine their emails and TLDs
    finding_calculations = {}
    for finding in findings:
        if finding['penalty'] <= PENALTIES['suspicious_tld']:
            if 'total' in finding_calculations:
                finding_calculations['total'] += finding['penalty']
            else:
                finding_calculations['total'] = finding['penalty']

            if 'domains' not in finding_calculations:
                finding_calculations['domains'] = []
            finding_calculations['domains'].append(finding['domains'])

            if 'evidence' in finding_calculations:
                finding_calculations['evidence'] += finding['evidence']
            else:
                finding_calculations['evidence'] = finding['evidence']

    high = len([f['penalty'] for f in findings if f['penalty'] == -15])
    low = len([f['penalty'] for f in findings if f['penalty'] == 0])

    # Step 3: Then return one finding with one penalty that lists them all.
    if 'total' in finding_calculations and finding_calculations['total'] <= PENALTIES['suspicious_tld']:
        return make_finding(
            name="suspicious_tld",
            bad_tld_count=len(finding_calculations['domains']),
            penalty_sum=finding_calculations['total'],
            penalty=PENALTIES['suspicious_tld'],
            reason=f"Contact email uses high-risk domain ({', '.join(finding_calculations['domains'])})",
            evidence=finding_calculations['evidence'],
            severity="high" if high >= 1 else "low"
        )
    return make_finding(
        name="suspicious_tld",
        penalty=0,
        reason="No suspicious TLDs found",
        bad_tld_count=0,
        penalty_sum=0,
        evidence=[],
        severity="low"
    )


"""
    Steps to think through:
    1. Parse salary text into numbers. You’ll see $80k , 80,000, $40-50/hr, $4,000 weekly. 
    The re module does the work here. Write the regex against real postings you’ve collected, not imagined ones.
    2. Normalize to annual so you can compare like with like: hourly × 2080, weekly × 52, monthly × 12.
    3. Run the rules:
        - Range ratio: if max / min is over about 2, flag it.
        - Ceiling: annualized pay above some threshold for an entry-level or “no experience” title gets flagged.
        - Keyword scan for the vague and commission-only phrases.
    4. Return the flags with weights and a short human-readable reason, such as “Range spans 5x ($50k–$250k)”. 
    Those reasons are what makes the UI useful.
"""


def check_salary(posting):
    # pattern = r"\$[0-9.]+(?:-[0-9.]+)?\/hr|\$[0-9,]+\s?(?:weekly|monthly)|\$[0-9,]+[kK]?|[0-9,]+[kK]?\s?(?:USD|usd)|[0-9,]{4,}"
    # salaries = re.findall(pattern, posting.text)
    # print('salaries', salaries)
    state = salary_graph.invoke({
        "text": posting.text,
    })

    analysis = state['salary_analysis']
    final = analysis.penalty

    evidence_list = []
    if analysis and \
            hasattr(analysis, 'commission_only') and \
            analysis.commission_only is not None and \
            hasattr(analysis.commission_only, 'reason') and \
            analysis.commission_only.reason:
        evidence_list.append(f"Commission: {analysis.commission_only.reason}")
    if analysis and analysis.company is not None and hasattr(analysis, 'company'):
        evidence_list.append(f"Company: {analysis.company}")
    if analysis and analysis.title is not None and hasattr(analysis, 'title'):
        evidence_list.append(f"Title: {analysis.title}")
    if (analysis and
            analysis.vague_pay is not None and
            hasattr(analysis, 'vague_pay') and
            analysis.vague_pay.reason is not None):
        evidence_list.append(f"Vague Pay: {analysis.vague_pay.reason}")

    return make_finding(
        name="salary",
        penalty=final,
        reason=analysis.reason,
        salary_analysis=analysis.model_dump(),
        severity="high",
        evidence=evidence_list,
    )


def check_ssl_validity(posting):
    """Check every distinct domain from the email and returns one finding that covers them all. """
    domains = []
    if posting and posting.post_details and hasattr(posting.post_details, 'emails'):
        domains = [get_domain_or_subdomain(d.split('@')[1]) for d in posting.post_details.emails]

    port: int = 443
    unique_domains = list(dict.fromkeys(domains))
    initial_results = list(check_ssl_status(domain, port, i) for i, domain in enumerate(unique_domains))

    final_result = {}
    if initial_results:
        for result in initial_results:
            # Create dictionary keys if it is not yet set
            if 'domain_results' not in final_result:
                final_result['domain_results'] = []
            if 'domains' not in final_result:
                final_result['domains'] = []
            if 'risk_domains' not in final_result:
                final_result['risk_domains'] = []
            if 'penalty' not in final_result:
                final_result['penalty'] = 0
            if 'evidence' not in final_result:
                final_result['evidence'] = []

            if result['penalty'] <= -20:
                final_result['penalty'] = result['penalty']
                final_result['domains'].append(result['hostname'])
                final_result['reason'] = result['reason']
                final_result['domain_results'].append(result)
                final_result['risk_domains'].append(result['hostname'])
                final_result['evidence'].append(f"{result['hostname']}: {result['reason']}")
            elif result['penalty'] <= -15:
                if final_result['penalty'] != -20:
                    final_result['penalty'] = result['penalty']
                    final_result['reason'] = result['reason']
                final_result['domains'].append(result['hostname'])
                final_result['risk_domains'].append(result['hostname'])
                final_result['domain_results'].append(result)
                final_result['evidence'].append(f"{result['hostname']}: {result['reason']}")
            else:
                if final_result['penalty'] != -20 and final_result['penalty'] != -15:
                    final_result['reason'] = result['reason']
                final_result['domains'].append(result['hostname'])
                final_result['domain_results'].append(result)

    if not final_result:
        return make_finding(
            name="ssl_validity",
            reason="No employer domain found, so SSL wasn’t checked",
            penalty=0,
            domains=[],
            risk_domains=[],
            domain_results=[],
            evidence=[],
            severity="low"
        )
    low = len([r['penalty'] for r in final_result['domain_results'] if r['penalty'] == 0])
    medium = len([r['penalty'] for r in final_result['domain_results'] if r['penalty'] == -15])
    high = len([r['penalty'] for r in final_result['domain_results'] if r['penalty'] == -20])

    return make_finding(
        name="ssl_validity",
        reason=final_result['reason'],
        penalty=final_result['penalty'],
        domains=final_result['domains'],
        risk_domains=final_result['risk_domains'],
        domain_results=final_result['domain_results'],
        evidence=final_result['evidence'],
        severity="high" if high >= 1 else ("medium" if medium >= 1 else "low"),
    )
