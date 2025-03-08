from django.urls import path
from . import views

from django.conf import settings 
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('', views.inicio, name = 'inicio'),
    path('usuarios/', views.usuarios, name = 'usuarios'),
    path('usuarios/crear', views.crear_usuario, name = 'crear'),
    path('usuarios/eliminar/<int:id>', views.eliminar_usuario, name = 'eliminar'),
    path('usuarios/editar/<int:id>', views.editar_usuario, name = 'editar'),
    path('usuarios/restablecer_contrasena/<int:id>', views.restablecer_contrasena, name='restablecer_contrasena'),

    path('inventario/', views.inventario, name = 'inventario'), 
    path('inventario/crear', views.crear_inventario, name = 'crear_inventario'),
    path('inventario/editar', views.editar_inventario, name = 'editar_inventario'),
    path('inventario/eliminar/<int:id>', views.eliminar_inventario, name = 'eliminar_inventario'),
]