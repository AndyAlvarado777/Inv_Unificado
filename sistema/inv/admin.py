from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('correo', 'nombre', 'is_staff')
    ordering = ('correo',)
    fieldsets = (
        (None, {'fields': ('correo', 'password')}),
        ('Información personal', {'fields': ('nombre', 'departamento', 'puesto')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
