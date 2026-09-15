
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    model = User

    list_display = (
        "id",
        "name",
        "email",
        "phone",
        "role",
        "is_verified",
        "is_active",
        "created_at",
    )

    list_filter = (
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "name",
        "email",
        "phone",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                )
            },
        ),

        (
            "Personal Information",
            {
                "fields": (
                    "name",
                    "phone",
                )
            },
        ),

        (
            "Role & Verification",
            {
                "fields": (
                    "role",
                    "is_verified",
                )
            },
        ),

        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),

        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": (
                    "wide",
                ),

                "fields": (
                    "name",
                    "email",
                    "phone",
                    "password1",
                    "password2",
                    "role",
                    "is_verified",
                ),
            },
        ),
    )
