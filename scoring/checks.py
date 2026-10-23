from .domains import get_registered_domain, get_hostname
from .rdap import get_domain_age_days
import re

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
        return {"name": "domain_age", "penalty": 0, "reason": "Couldn't check domain age"}
    elif days < 30:
        return {"name": "domain_age", "penalty": -35, "reason": f"Domain registered {days} days ago"}
    elif days < 180:
        return {"name": "domain_age", "penalty": -20, "reason": f"Domain registered {days} days ago"}
    else:
        return {"name": "domain_age", "penalty": 0, "reason": f"Domain is {days // 365} years old"}


FREE_EMAIL_PROVIDERS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
                        "aol.com", "icloud.com", "proton.me", "protonmail.com"}

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
