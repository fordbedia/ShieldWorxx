from django.db import models
from django.utils import timezone
from datetime import timedelta, timezone as dt_timezone

import hashlib
from urllib.parse import urlsplit, urlunsplit


def normalize_url(url: str) -> str:
    p = urlsplit(url.strip())
    path = p.path.rstrip("/") or "/"
    return urlunsplit((p.scheme.lower(),
                       p.netloc.lower(), path, p.query, ""))

def hash_url(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()

CACHE_TTL = timedelta(days=30)  # how long a scan stays reusable

class JobManager(models.Manager):
    def create_or_new_from_url(
            self,
            url: str,
            basic: list,
            advanced: list,
            score: dict
    ) -> models.Model:
        job_manager = self.for_url(url)
        if not job_manager.exists():
            return self.create(
                url=normalize_url(url),
                findings=basic+advanced,
                score=score,
                total=score.get("total", 0),
                verdict=score.get("verdict", ""),
                expires_at=timezone.now() + CACHE_TTL
            )
        else:
            model = job_manager.first()
            if job_manager.is_expired():
                model.expired = True
            return model

    def get_or_scan(self, url: str, scanner) ->tuple["Job", bool]:
          job = self.latest_for_url(url)
          if job is not None:
              return job, False
          basic, advanced, score = scanner(url)
          return self.create_or_new_from_url(url, basic=basic, advanced=advanced, score=score), True

class JobQuerySet(models.QuerySet):
     def active(self):
        now = timezone.now()
        return self.filter(deleted_at__isnull=True).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=now))

     def for_job(self, url: str):
        return self.filter(url=normalize_url(url))

     def has_job(self, url: str):
        return self.active().filter(url=normalize_url(url))

     def is_expired(self):
         return self.filter(expires_at__lte=timezone.now()).exists()

     # def for_url(self, url: str) -> str:
     #     return self.filter(url=normalize_url(url))

     def for_url(self, url: str):
        return self.filter(url_hash=hash_url(url))

     def latest_for_url(self, url: str):
        return self.active().for_url(url).order_by("-created_at").first()


# Create your models here.
class Job(models.Model):
    objects = JobManager.from_queryset(JobQuerySet)()

    expired: bool = False

    url = models.URLField(max_length=2048)
    url_hash = models.CharField(max_length=64, unique=True, editable=False)
    findings = models.JSONField(default=list)
    score = models.JSONField(default=dict)
    total = models.PositiveSmallIntegerField(null=True,
                                             db_index=True)  # copied from score["total"] so it can   │be filtered and sorted                 │
    verdict = models.CharField(max_length=100, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
      self.url_hash = hash_url(self.url)
      super().save(*args, **kwargs)