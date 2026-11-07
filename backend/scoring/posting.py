from dataclasses import dataclass

@dataclass
class PostDetails:
    domain: str
    emails: list[str]

@dataclass
class PostJob:
    salary: int = 0
    job_title: str = ""
    location: str = ""

@dataclass()
class EmployerJobPost:
    company: str | None
    host: str | None

@dataclass
class Post:
    url: str
    post_details: PostDetails | None = None
    post_job: PostJob | None = None
    employer_job: EmployerJobPost | None = None
    text: str = ""
    company_name: str = ""

@dataclass
class SalaryMention:
    raw: str          # "$40-50/hr"  ← becomes your evidence
    min: float
    max: float
    period: str       # "hour" | "week" | "month" | "year"