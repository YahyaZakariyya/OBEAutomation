from django.contrib import admin
from users.models import CustomUser
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('role',)
    list_per_page = 20  # Set pagination to show 25 entries per page
    # list_editable = ('first_name','last_name')
    # ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

CustomUser._meta.verbose_name = "User"
CustomUser._meta.verbose_name_plural = "Users"