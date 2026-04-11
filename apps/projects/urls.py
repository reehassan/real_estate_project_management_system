from django.urls import path
from . import views

app_name = 'projects'                                # namespace — use as projects:list in templates

urlpatterns = [
    path('', views.project_list_view, name='list'),  # /projects/

    # new — slug captured from URL and passed to view as kwarg
    path('<slug:slug>/plots/', views.plot_list_view, name='plot_list'),
]