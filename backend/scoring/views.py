from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from .services import scan_job
from .models import Job



# Create your views here.
class ValidateAll(APIView):
    def get(self, request, job_url):
        job = Job.objects
        has_job =job.active().for_job(url=job_url).exists()
        if not has_job:
            basic, advanced, score  = scan_job(job_url)
            job.create_or_new_from_url(
                url=job_url,
                basic=basic,
                advanced=advanced,
                score=score
            )
            return Response({"score": score, "findings": basic + advanced})
        # Show and return the model
        job, scanned = Job.objects.get_or_scan(job_url, scanner=scan_job)
        return Response({"score": job.score, "findings":job.findings, "cached": not scanned})

