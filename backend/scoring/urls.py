from django.urls import path

from .views import ValidateAll

urlpatterns = [
    path('run/<path:job_url>', ValidateAll.as_view()),
]