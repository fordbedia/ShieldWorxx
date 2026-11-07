import tldextract
import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from dataclasses import dataclass

def get_hostname(url):
    parsed = urlparse(url)
    hostname = parsed.hostname
    return hostname

def get_registered_domain(hostname):
    hostname = tldextract.extract(hostname).registered_domain
    return hostname

def get_domain_or_subdomain(hostname):
    extracted = tldextract.extract(hostname)

    # If a subdomain exists, combine it with the registered domain
    if extracted.subdomain:
        return f"{extracted.subdomain}.{extracted.registered_domain}"

    # If no subdomain exists, return just the registered domain
    return extracted.registered_domain

def get_domain_tld(domain) -> str:
    return f"."+tldextract.extract(domain).suffix.lower().strip()