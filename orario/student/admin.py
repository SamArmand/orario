from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from models import Student

class StudentAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Student info'), {'fields': ('option', 'courses_taken', 'courses_selected')})
    )
    filter_horizontal = ('groups', 'user_permissions', 'courses_taken', 'courses_selected')

admin.site.register(Student, StudentAdmin)
