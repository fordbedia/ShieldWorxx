import requests
from .rdap import HEADERS
from bs4 import BeautifulSoup

def fetch_text(url)-> str | None:
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )
        emails = set()
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)
            for email in soup.find_all("a", href=True):
                link = email['href']
                if link.lower().startswith("mailto:"):
                    emails.add(link.lower().removeprefix("mailto:").split("?")[0].strip())
            return text + " " + " ".join(emails)
    except Exception:
        return None
    return None