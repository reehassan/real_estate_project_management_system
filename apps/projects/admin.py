# projects/admin.py
from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display  = ('name', 'city', 'project_type', 'sub_type', 'status', 'start_date', 'is_deleted')
    list_filter   = ('project_type', 'status', 'city', 'is_deleted')
    search_fields = ('name', 'city', 'location')
    ordering      = ('-start_date',)

    prepopulated_fields = {'slug': ('name',)}
    readonly_fields     = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'slug', 'logo', 'description')
        }),
        ('Location', {
            'fields': ('location', 'city')
        }),
        ('Classification', {
            'fields': ('project_type', 'sub_type')
        }),
        ('Project Details', {
            'fields': ('status', 'start_date', 'total_area', 'area_unit')
        }),
        ('System', {
            'fields': ('is_deleted', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['soft_delete', 'restore']

    @admin.action(description='Soft delete selected projects')
    def soft_delete(self, request, queryset):
        queryset.update(is_deleted=True)

    @admin.action(description='Restore selected projects')
    def restore(self, request, queryset):
        queryset.update(is_deleted=False)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)