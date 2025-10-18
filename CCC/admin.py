from django.contrib import admin
from django.utils import timezone
from .models import Club, ClubApplication

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'member_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('members',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Total Members'


@admin.action(description='Approve selected applications')
def approve_applications(modeladmin, request, queryset):
    updated = 0
    for app in queryset.filter(status=ClubApplication.STATUS_PENDING):
        app.status = ClubApplication.STATUS_APPROVED
        app.reviewed_at = timezone.now()
        app.reviewer = request.user
        app.save()
        app.club.members.add(app.user)
        updated += 1
    modeladmin.message_user(request, f"Approved {updated} application(s).")


@admin.action(description='Reject selected applications')
def reject_applications(modeladmin, request, queryset):
    updated = 0
    for app in queryset.filter(status=ClubApplication.STATUS_PENDING):
        app.status = ClubApplication.STATUS_REJECTED
        app.reviewed_at = timezone.now()
        app.reviewer = request.user
        app.save()
        updated += 1
    modeladmin.message_user(request, f"Rejected {updated} application(s).")


@admin.register(ClubApplication)
class ClubApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'status', 'created_at', 'reviewed_at', 'reviewer')
    list_filter = ('status', 'club', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'club__name')
    actions = (approve_applications, reject_applications)
    readonly_fields = ('created_at', 'reviewed_at', 'reviewer')
    raw_id_fields = ('user', 'club', 'reviewer')
    ordering = ('-created_at',)
