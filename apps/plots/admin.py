from django.contrib import admin
from .models import Plot, PlotAuditLog


# ─────────────────────────────────────────────────────────────────
# Inline — shows audit history inside the Plot detail page
# ─────────────────────────────────────────────────────────────────
class PlotAuditLogInline(admin.TabularInline):
    model           = PlotAuditLog
    extra           = 0
    can_delete      = False
    show_change_link = False
    readonly_fields = ('action', 'changed_by', 'changed_at', 'field_name', 'old_value', 'new_value', 'note')

    def has_add_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────────────────────────
# Main Plot Admin
# ─────────────────────────────────────────────────────────────────
@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):

    # ── List View ─────────────────────────────────────────────────
    list_display  = ('plot_number', 'project', 'category', 'status',
                     'area', 'area_unit', 'price', 'is_corner',
                     'created_by', 'updated_by', 'updated_at')
    list_filter   = ('status', 'category', 'is_corner', 'is_deleted', 'project')
    search_fields = ('plot_number', 'project__name', 'description')
    ordering      = ('project', 'plot_number')

    # ── Detail View ───────────────────────────────────────────────
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    inlines         = [PlotAuditLogInline]

    fieldsets = (
        ('Plot Identity', {
            'fields': ('project', 'plot_number', 'category')
        }),
        ('Measurements', {
            'fields': ('area', 'area_unit')
        }),
        ('Pricing', {
            'fields': ('price',)
        }),
        ('Details', {
            'fields': ('description', 'is_corner')
        }),
        ('Status', {
            'fields': ('status', 'is_deleted')
        }),
        ('Audit Info', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['soft_delete', 'restore']

    # ── Auto-capture who is saving ────────────────────────────────
    def save_model(self, request, obj, form, change):
        # Snapshot old values BEFORE saving
        old_obj = None
        if change:
            try:
                old_obj = Plot.objects.get(pk=obj.pk)
            except Plot.DoesNotExist:
                pass

        # Stamp who is performing this action
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user

        # Save to database
        super().save_model(request, obj, form, change)

        # Write audit log AFTER save
        if not change:
            # CREATE event — single log row, no field comparison needed
            PlotAuditLog.objects.create(
                plot       = obj,
                action     = PlotAuditLog.Action.CREATED,
                changed_by = request.user,
                note       = 'Plot created via admin panel'
            )
        elif old_obj:
            # UPDATE event — compare each field, log only actual changes
            fields_to_watch = [
                'plot_number', 'category', 'status',
                'area', 'area_unit', 'price',
                'description', 'is_corner', 'is_deleted'
            ]
            for field in fields_to_watch:
                old_val = str(getattr(old_obj, field))
                new_val = str(getattr(obj, field))
                if old_val != new_val:
                    PlotAuditLog.objects.create(
                        plot       = obj,
                        action     = PlotAuditLog.Action.UPDATED,
                        changed_by = request.user,
                        field_name = field,
                        old_value  = old_val,
                        new_value  = new_val,
                    )

    # ── Soft Delete Action ────────────────────────────────────────
    @admin.action(description='Soft delete selected plots')
    def soft_delete(self, request, queryset):
        for obj in queryset:
            obj.is_deleted = True
            obj.updated_by = request.user
            obj.save()
            PlotAuditLog.objects.create(
                plot       = obj,
                action     = PlotAuditLog.Action.DELETED,
                changed_by = request.user,
                field_name = 'is_deleted',
                old_value  = 'False',
                new_value  = 'True',
                note       = 'Soft deleted via admin panel'
            )

    # ── Restore Action ────────────────────────────────────────────
    @admin.action(description='Restore selected plots')
    def restore(self, request, queryset):
        for obj in queryset:
            obj.is_deleted = False
            obj.updated_by = request.user
            obj.save()
            PlotAuditLog.objects.create(
                plot       = obj,
                action     = PlotAuditLog.Action.RESTORED,
                changed_by = request.user,
                field_name = 'is_deleted',
                old_value  = 'True',
                new_value  = 'False',
                note       = 'Restored via admin panel'
            )

    # ── Hide soft-deleted plots from list by default ──────────────
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


# ─────────────────────────────────────────────────────────────────
# Standalone Audit Log Admin — fully read-only
# ─────────────────────────────────────────────────────────────────
@admin.register(PlotAuditLog)
class PlotAuditLogAdmin(admin.ModelAdmin):

    list_display  = ('plot', 'action', 'field_name', 'old_value',
                     'new_value', 'changed_by', 'changed_at')
    list_filter   = ('action', 'changed_by', 'changed_at')
    search_fields = ('plot__plot_number', 'plot__project__name', 'changed_by__username')
    ordering      = ('-changed_at',)
    readonly_fields = ('plot', 'action', 'changed_by', 'changed_at',
                       'field_name', 'old_value', 'new_value', 'note')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False