from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')), 
    path('projects/', include('apps.projects.urls', namespace='projects')),
    path('plots/',include('apps.plots.urls')),
]