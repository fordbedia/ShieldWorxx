from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from scoring.posting import Post
from scoring.engine import run_all_checks

validate_url = URLValidator(schemes=["http", "https"])

# Create your views here.
class ValidateAll(APIView):
    def get(self, request, job_url):
        try:
            validate_url(job_url)
        except ValidationError:
            return Response({"error": "Invalid URL"}, status=400)
        basic, score, advanced = run_all_checks(Post(url=job_url))
        return Response({"score": score, "findings": basic + advanced})