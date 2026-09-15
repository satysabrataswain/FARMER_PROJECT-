
from django.contrib import admin

from .models import (
    Complaint,
    ComplaintAttachment,
    ComplaintMessage,
)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = [
        "complaint_number",
        "customer",
        "complaint_type",
        "priority",
        "status",
        "assigned_admin",
        "assigned_seller",
        "created_at",
    ]

    list_filter = [
        "complaint_type",
        "priority",
        "status",
        "created_at",
    ]

    search_fields = [
        "complaint_number",
        "subject",
        "description",
        "customer__email",
        "customer__name",
    ]

    readonly_fields = [
        "complaint_number",
        "created_at",
        "updated_at",
        "resolved_at",
        "closed_at",
    ]


@admin.register(ComplaintAttachment)
class ComplaintAttachmentAdmin(admin.ModelAdmin):

    list_display = [
        "complaint",
        "uploaded_by",
        "file",
        "created_at",
    ]

    list_filter = [
        "created_at",
    ]

    search_fields = [
        "complaint__complaint_number",
        "uploaded_by__email",
    ]

    readonly_fields = [
        "created_at",
    ]


@admin.register(ComplaintMessage)
class ComplaintMessageAdmin(admin.ModelAdmin):

    list_display = [
        "complaint",
        "sender",
        "is_internal",
        "created_at",
    ]

    list_filter = [
        "is_internal",
        "created_at",
    ]

    search_fields = [
        "complaint__complaint_number",
        "sender__email",
        "message",
    ]

    readonly_fields = [
        "created_at",
    ]
