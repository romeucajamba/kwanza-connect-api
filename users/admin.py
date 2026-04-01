from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, IdentityDocument, UserSecurity, UserReport


class IdentityInline(admin.StackedInline):
    model = IdentityDocument
    fk_name = 'user'
    extra = 0
    readonly_fields = ['submitted_at', 'reviewed_at']


class SecurityInline(admin.StackedInline):
    model = UserSecurity
    extra = 0
    readonly_fields = ['email_verified_at', 'locked_until', 'password_changed_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['email', 'full_name', 'country_code', 'is_active',
                     'is_verified', 'verification_status', 'date_joined']
    list_filter   = ['is_active', 'is_verified', 'verification_status', 'country_code']
    search_fields = ['email', 'full_name', 'phone']
    ordering      = ['-date_joined']
    inlines       = [IdentityInline, SecurityInline]

    fieldsets = (
        ('Credenciais',    {'fields': ('email', 'password')}),
        ('Dados pessoais', {'fields': ('full_name', 'phone', 'country_code',
                                       'city', 'address', 'occupation', 'bio', 'avatar')}),
        ('Estado',         {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'is_verified', 'is_available', 'verification_status')}),
        ('Preferências',   {'fields': ('preferred_give_currency', 'preferred_want_currency')}),
        ('Actividade',     {'fields': ('last_seen', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2'),
        }),
    )
    readonly_fields = ['last_seen', 'date_joined']


@admin.register(IdentityDocument)
class IdentityDocumentAdmin(admin.ModelAdmin):
    list_display  = ['user', 'doc_type', 'doc_number', 'status', 'submitted_at']
    list_filter   = ['status', 'doc_type']
    search_fields = ['user__email', 'user__full_name', 'doc_number']
    actions       = ['approve_documents', 'reject_documents']

    def approve_documents(self, request, queryset):
        from django.utils import timezone
        for doc in queryset:
            doc.status = 'approved'
            doc.reviewed_at = timezone.now()
            doc.reviewed_by = request.user
            doc.save()
            doc.user.is_verified = True
            doc.user.verification_status = 'approved'
            doc.user.save(update_fields=['is_verified', 'verification_status'])
    approve_documents.short_description = 'Aprovar documentos seleccionados'

    def reject_documents(self, request, queryset):
        queryset.update(status='rejected')
    reject_documents.short_description = 'Rejeitar documentos seleccionados'


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported', 'reason', 'status', 'created_at']
    list_filter  = ['status', 'reason']