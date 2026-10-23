import requests
from datetime import datetime, timezone

HEADERS = {
    "User-Agent": "jobguard/0.1 (learning project; contact: you@example.com)"
}

def get_domain_age_days(domain) -> str | None:
    """'indeed.com' -> a big number like 7000. Any failure -> None."""
    # TODO:
    # 1. requests.get(f"https://rdap.org/domain/{domain}", timeout=10)
    # 2. if status isn't 200 -> return None
    # 3. loop over resp.json()["events"], find eventAction == "registration"
    # 4. parse its eventDate with datetime.fromisoformat
    # 5. return (now - registered).days
    # Wrap it all in try/except -> return None
    try:
        response = requests.get(f"https://rdap.org/domain/{domain}", timeout=10, headers=HEADERS)
        if response.status_code != 200:
            print("DEBUG:", domain, response.status_code, response.url)
            print(response.text[:300])
            return None
        events = response.json()['events']
        event = next((e for e in events if e['eventAction'] == 'registration'), None)
        if event is None:
            return None
        now = datetime.now(timezone.utc)
        registered = (now - datetime.fromisoformat(event['eventDate'])).days
    except Exception:
        return None
    return registered