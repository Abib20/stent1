from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm

from .models import CustomUser, Report
from django.contrib.admin import AdminSite


class ReportInLine(admin.TabularInline):
    model = Report
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = [
        ReportInLine,
    ]
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    fieldsets = (
        ('Персональная информация', {
            'fields': (('first_name', 'last_name', 'patronymic'), ('sex', 'age'), ('phone', 'status'))
        }),
        ('Медицинская информация', {
            'fields': (('hospital', 'section'), 'iin', ('pcr', 'isVaccianted'), 'period', 'days')
        }),
        ('Информация о пользователе', {
            'fields': ('username', 'password')
        }),
        ('Права доступа', {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),

    )
    list_display = ['username', 'first_name', 'last_name', 'patronymic', 'sex', 'age',
                    'hospital', 'section', 'phone', 'iin', 'pcr', 'isVaccianted',  'status', 'period', 'days']
    search_fields = list_display


class MyAdminSite(AdminSite):
    site_header = 'Администрирование системы опрашивания пациентов'


admin_site = MyAdminSite(name='myadmin')
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Report)
