from .domains import get_registered_domain, get_hostname, get_domain_tld
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
        return {"name": "domain_age", "domain": domain, "penalty": 0, "reason": "Couldn't check domain age"}
    elif days < 30:
        return {"name": "domain_age", "domain": domain, "penalty": -35, "reason": f"Domain registered {days} days ago"}
    elif days < 180:
        return {"name": "domain_age", "domain": domain, "penalty": -20, "reason": f"Domain registered {days} days ago"}
    else:
        return {"name": "domain_age", "domain": domain, "penalty": 0, "reason": f"Domain is {days // 365} years old"}

def check_recruiter_email(posting):
    emails = [e.rstrip(".") for e in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", posting.text)]
    free = [e for e in emails if e.split("@")[1].lower() in FREE_EMAIL_PROVIDERS]
    company = [e for e in emails if e not in free]
    if not emails:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": 0, "reason": "No recruiter email in posting"}
    elif free and company:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": -15, "reason": f"Posting lists a company email ({', '.join(company)}) but also a free address ({', '.join(free)})"}
    elif free:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": -15, "reason": f"Recruiter uses a free email address ({', '.join(free)})"}
    else:
        return {"name": "recruiter_email", "details": {"free": free, "company": company}, "penalty": 0, "reason": f"Recruiter email uses a company domain ({', '.join(company)})"}

def check_suspicious_requests(posting):
    state = fraud_graph.invoke({
        "text": posting.text
    })

    state.pop("text", None)
    return make_finding(
        name="suspicious_requests",
        **state
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
            evidence=[]
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

    # Step 3: Then return one finding with one penalty that lists them all.
    if 'total' in finding_calculations and finding_calculations['total'] <= PENALTIES['suspicious_tld']:
        return make_finding(
            name="suspicious_tld",
            bad_tld_count=len(finding_calculations['domains']),
            penalty_sum=finding_calculations['total'],
            penalty=PENALTIES['suspicious_tld'],
            reason=f"Contact email uses high-risk domain ({', '.join(finding_calculations['domains'])})",
            evidence=finding_calculations['evidence'],
        )
    return make_finding(
        name="suspicious_tld",
        penalty=0,
        reason="No suspicious TLDs found",
        bad_tld_count=0,
        penalty_sum=0,
        evidence=[]
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

    return make_finding(
        name="salary",
        penalty=final,
        reason=analysis.reason,
        salary_analysis=analysis.model_dump(),
    )

def check_ssl_validity(posting):
    context = ssl.create_default_context()
    print('posting.post_details', posting.post_details.emails)
    """Check every distinct domain from the email and returns one finding that covers them all. """
    domains = []
    if posting and posting.post_details and hasattr(posting.post_details, 'emails'):
        domains = [get_registered_domain(d.split('@')[1]) for d in posting.post_details.emails]
    print('domains', domains)

    hostname: str = get_registered_domain(get_hostname(posting.url))
    port: int = 443

    try:
        # Establish a network connection and wrap it with SSL
        with socket.create_connection((hostname, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                # If wrap_socket succeeds, the SSL certificate is VALID
                # Now extract metadata like the expiration date
                cert = ssock.getpeercert()

                # Parse the expiration date string (e.g., 'Jan 24 12:00:00 2027 GMT')
                expiry_str = cert["notAfter"]
                expiry_date = datetime.strptime(
                    expiry_str, "%b %d %H:%M:%S %Y %Z"
                ).replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                days_left = (expiry_date - current_time).days

                if days_left <= 0:
                    return make_finding(
                        name="ssl_validity",
                        reason=f"Company website's SSL certificate has expired ({hostname}).",
                        penalty=PENALTIES['expired_ssl'],
                    )

                return make_finding(
                    name="ssl_validity",
                    reason=f"Company website has a valid SSL certificate ({hostname}).",
                    evidence=[f"Expires on: {expiry_str} ({days_left} days left)", f"SSL Issued to: {dict(cert['subject'][-1])['commonName']}"],
                    penalty=0
                )

    except ssl.SSLCertVerificationError as e:
        return make_finding(
            name="ssl_validity",
            reason=f"SSL certificate isn't from a trusted issuer ({hostname}).",
            penalty=PENALTIES['self_signed_or_untrusted_ca'],
        )
    except socket.timeout:
        return make_finding(
            name="ssl_validity",
            reason=f"Couldn't check SSL certificate ({hostname} didn't respond).",
            penalty=0
        )
    except Exception as e:
        return make_finding(
            name="ssl_validity",
            reason=f"Couldn't check SSL certificate ({hostname})",
            penalty=0
        )