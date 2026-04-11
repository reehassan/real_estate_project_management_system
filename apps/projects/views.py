from django.shortcuts import render, get_object_or_404
from .models import Project
from apps.plots.models import Plot


def project_list_view(request):
    """
    Fetches all non-deleted projects and sends them to the template.
    URL: /projects/
    Template: projects/project_list.html
    """
    projects = Project.objects.filter(is_deleted=False).order_by('-start_date')

    context = {
        'projects'   : projects,
        'total_count': projects.count(),
    }

    return render(request, 'projects/project_list.html', context)


# ─────────────────────────────────────────────────────────────────
def plot_list_view(request, slug):
    """
    Fetches one project by slug, then all its non-deleted plots.
    URL: /projects/<slug>/plots/
    Template: projects/plot_list.html
    """

    # fetch the project — auto 404 if slug doesn't exist
    project = get_object_or_404(Project, slug=slug, is_deleted=False)

    # base queryset — only plots belonging to this project
    plots = Plot.objects.filter(
        project    = project,
        is_deleted = False
    )

    # ── Optional Filters From URL Query Params ────────────────────
    # example: /projects/dreamland/plots/?status=AVAILABLE&category=RESIDENTIAL
    status   = request.GET.get('status', '')      # '' means no filter applied
    category = request.GET.get('category', '')

    if status:
        plots = plots.filter(status=status)

    if category:
        plots = plots.filter(category=category)

    # ── Summary Counts For The Header ─────────────────────────────
    all_plots   = Plot.objects.filter(project=project, is_deleted=False)

    context = {
        'project'        : project,
        'plots'          : plots,
        'total_count'    : all_plots.count(),
        'available_count': all_plots.filter(status='AVAILABLE').count(),
        'booked_count'   : all_plots.filter(status='BOOKED').count(),
        'sold_count'     : all_plots.filter(status='SOLD').count(),
        'selected_status'  : status,      # to keep filter selected in template
        'selected_category': category,
        'status_choices' : Plot.PlotStatus.choices,    # for filter dropdown
        'category_choices': Plot.PlotCategory.choices, # for filter dropdown
    }

    return render(request, 'projects/plot_list.html', context)