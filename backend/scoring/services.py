from scoring.engine import run_all_checks
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from scoring.posting import Post

validate_url = URLValidator(schemes=["http", "https"])

def scan_job(job_url):
    try:
        validate_url(job_url)
    except ValidationError:
        raise ValidationError("Invalid URL")
    return run_all_checks(Post(url=job_url))
