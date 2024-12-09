from django.contrib import admin
from django.urls import path, re_path
from obesystem.views import AssessmentDataAPI, UpdateScoresAPI
from obesystem.views import ReactAppView  # This is the view that returns index.html

urlpatterns = [
    path('app/', ReactAppView.as_view(), name='react-app'),
    re_path(r'^app/.*$', ReactAppView.as_view()),  # catch-all for SPA routes
    path('api/get-assessment-data/', AssessmentDataAPI.as_view(), name='get-assessment-data'),
    path('api/update-scores/', UpdateScoresAPI.as_view(), name='update-scores'),
    path('', admin.site.urls),
]
