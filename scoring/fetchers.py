import requests
from .rdap import HEADERS
from bs4 import BeautifulSoup

def fetch_text(url)-> str | None:
    response = requests.get(
        url,
        headers=HEADERS
    )
    if response.status_code != 200:
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)
        return text
    return None