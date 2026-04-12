from django.contrib import admin
from django.utils.html import format_html
from .models import Customer


# ─────────────────────────────────────────────────────────────────
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    # ── List View ─────────────────────────────────────────────────
    list_display = (
        'photo_thumbnail',
        'get_full_name',
        'cnic',
        'phone',
        'city',
        'get_email',
        'documents_status',
        'is_deleted',
        'created_at',
    )
    list_filter   = ('city', 'is_deleted', 'created_at')
    search_fields = (
        'cnic',
        'phone',
        'city',
        'full_name',
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
    )
    ordering      = ('user__username',)
    list_per_page = 25

    # ── Read-Only Fields ──────────────────────────────────────────
    readonly_fields = (
        'photo_thumbnail',
        'photo_large',
        'cnic_front_preview',
        'cnic_back_preview',
        'agreement_preview',
        'get_email',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )

    # ── Form Layout ───────────────────────────────────────────────
    fieldsets = (

        (' User Account', {
            'fields'     : ('user', 'get_email'),
            'description': 'Login account linked to this customer profile.',
        }),

        (' Personal Information', {
            'fields': (
                'full_name',
                'cnic',
                'phone',
                'phone_alt',
            )
        }),

        (' Location', {
            'fields': ('address', 'city')
        }),

        (' Profile Photo', {
            'fields': (
                'profile_photo',
                'photo_large',
            )
        }),

        (' CNIC Documents', {
            'fields': (
                'cnic_front',
                'cnic_front_preview',
                'cnic_back',
                'cnic_back_preview',
            )
        }),

        (' Agreement', {
            'fields': (
                'agreement_copy',
                'agreement_preview',
            )
        }),

        (' Status', {
            'fields': ('is_deleted',)
        }),

        (' Audit Trail', {
            'fields' : (
                'created_by', 'created_at',
                'updated_by', 'updated_at',
            ),
            'classes': ('collapse',),
        }),

    )

    actions = ['soft_delete', 'restore']

    # ── List Column: Small Photo Thumbnail ────────────────────────
    @admin.display(description='Photo')
    def photo_thumbnail(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" width="40" height="40" '
                'style="border-radius:50%;object-fit:cover;'
                'border:2px solid #e2e8f0;">',
                obj.profile_photo.url
            )
        name    = obj.get_full_name()
        initial = name[0].upper() if name else '?'
        return format_html(
            '<div style="width:40px;height:40px;border-radius:50%;'
            'background:linear-gradient(135deg,#2563eb,#1d4ed8);'
            'color:white;display:flex;align-items:center;'
            'justify-content:center;font-weight:700;'
            'font-size:15px;border:2px solid #bfdbfe;">'
            '{}</div>',
            initial
        )

    # ── Detail View: Large Photo ──────────────────────────────────
    @admin.display(description='Current Photo')
    def photo_large(self, obj):
        if obj.profile_photo:
            return format_html(
                '<img src="{}" width="120" height="120" '
                'style="border-radius:12px;object-fit:cover;'
                'border:3px solid #e2e8f0;margin-top:6px;">',
                obj.profile_photo.url
            )
        return format_html(
            '<span style="color:#94a3b8;font-style:italic;">'
            'No photo uploaded</span>'
        )

    # ── CNIC Front Preview ────────────────────────────────────────
    @admin.display(description='CNIC Front Preview')
    def cnic_front_preview(self, obj):
        if obj.cnic_front:
            return format_html(
                '<img src="{}" style="max-width:320px;border-radius:10px;'
                'border:2px solid #e2e8f0;margin-top:6px;">',
                obj.cnic_front.url
            )
        return format_html(
            '<span style="color:#94a3b8;font-style:italic;">'
            'No CNIC front uploaded</span>'
        )

    # ── CNIC Back Preview ─────────────────────────────────────────
    @admin.display(description='CNIC Back Preview')
    def cnic_back_preview(self, obj):
        if obj.cnic_back:
            return format_html(
                '<img src="{}" style="max-width:320px;border-radius:10px;'
                'border:2px solid #e2e8f0;margin-top:6px;">',
                obj.cnic_back.url
            )
        return format_html(
            '<span style="color:#94a3b8;font-style:italic;">'
            'No CNIC back uploaded</span>'
        )

    # ── Agreement Preview ─────────────────────────────────────────
    @admin.display(description='Agreement File')
    def agreement_preview(self, obj):
        if obj.agreement_copy:
            return format_html(
                '<a href="{}" target="_blank" '
                'style="display:inline-block;padding:6px 14px;'
                'background:#2563eb;color:white;border-radius:6px;'
                'text-decoration:none;font-size:13px;margin-top:6px;">'
                '📄 View Agreement</a>',
                obj.agreement_copy.url
            )
        return format_html(
            '<span style="color:#94a3b8;font-style:italic;">'
            'No agreement uploaded</span>'
        )

    # ── Documents Status Column ───────────────────────────────────
    @admin.display(description='Docs')
    def documents_status(self, obj):
        """
        Shows which documents have been uploaded as colored dots.
        Green = uploaded. Red = missing.
        """
        def dot(uploaded):
            color = '#22c55e' if uploaded else '#ef4444'
            return f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{color};margin:0 2px;" title="{"uploaded" if uploaded else "missing"}"></span>'

        html = (
            dot(bool(obj.profile_photo)) +
            dot(bool(obj.cnic_front))    +
            dot(bool(obj.cnic_back))     +
            dot(bool(obj.agreement_copy))
        )
        legend = 'Photo · CNIC Front · CNIC Back · Agreement'
        return format_html(
            '<div title="{}">{}</div>', legend, html
        )

    # ── Email From Linked User ────────────────────────────────────
    @admin.display(description='Email')
    def get_email(self, obj):
        return obj.user.email

    # ── Auto-stamp Created/Updated By ─────────────────────────────
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # ── Bulk Actions ──────────────────────────────────────────────
    @admin.action(description='Soft delete selected customers')
    def soft_delete(self, request, queryset):
        count = queryset.update(is_deleted=True)
        self.message_user(request, f'{count} customer(s) soft deleted.')

    @admin.action(description='Restore selected customers')
    def restore(self, request, queryset):
        count = queryset.update(is_deleted=False)
        self.message_user(request, f'{count} customer(s) restored.')

    # ── Hide Soft-Deleted By Default ─────────────────────────────
    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)