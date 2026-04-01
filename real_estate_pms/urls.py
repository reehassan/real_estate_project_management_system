from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')), # this connects your view
    path('projects/', include('apps.projects.urls')),  
]