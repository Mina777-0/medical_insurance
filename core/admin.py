from django.contrib import admin
from .models import CustomUser, MedicalInsurance, FamilyInsurance
from .forms import CustomChangeForm, CustomCreationForm
from django.contrib.auth.admin import UserAdmin


class CustomUserAdmin(UserAdmin):
    form= CustomChangeForm
    add_form= CustomCreationForm
    model= CustomUser
    list_display= ["first_name", "last_name", "last_login"]
    list_filter= ["email", "is_staff", "is_active"]

    fieldsets= (
        (None, {"fields": ("email", "password")}),
        ("permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")})
    )

    add_fieldsets= (
        (
            None, {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_active", "is_staff")
            }
        )
    )

    search_fields= ("email",)
    ordering= ("email",)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MedicalInsurance)
admin.site.register(FamilyInsurance)
