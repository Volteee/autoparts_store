from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone',
                'address'
            )
        }),
        ('Настройки доставки', {'fields': ('delivery_preference',)}),
        ('Роли и права', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'password1',
                'password2',
                'role',
                'email',
                'first_name',
                'last_name'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)