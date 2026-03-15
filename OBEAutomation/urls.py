from django.contrib import admin
from django.urls import path, include
from users.views import home_view


urlpatterns = [
    path('', home_view, name='home'),
    path('dashboard/', admin.site.urls),
    path('api/', include('api.urls')),
    path('assessments/', include('assessments.urls')),
    path('results/', include('results.urls')),
]
