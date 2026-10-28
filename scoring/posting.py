from dataclasses import dataclass

@dataclass
class PostDetails:
    domain: str
    emails: list[str]

@dataclass
class Post:
    url: str
    post_details: PostDetails | None = None
    text: str = ""
    company_name: str = ""