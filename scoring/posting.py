from dataclasses import dataclass

@dataclass
class Post:
    url: str
    text: str = ""
    company_name: str = ""