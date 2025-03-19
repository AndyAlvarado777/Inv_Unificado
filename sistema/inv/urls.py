from django.urls import path
from . import views


from django.conf import settings 
from django.contrib.staticfiles.urls import static

urlpatterns = [
    path('', views.inicio, name = 'inicio'),
    path('usuarios/perfil',views.perfil, name = 'perfil'),
    path('accounts/login/', views.login_view, name='custom_login'),
    path('logout/', views.logout_view, name='logout'),
    path('usuarios/', views.usuarios, name = 'usuarios'),
    path('usuarios/crear', views.crear_usuario, name = 'crear'),
    path('usuarios/eliminar/<int:id>', views.eliminar_usuario, name = 'eliminar'),
    path('usuarios/editar/<int:id>', views.editar_usuario, name = 'editar'),
    path('usuarios/restablecer_contrasena/<int:id>', views.restablecer_contrasena, name='restablecer_contrasena'),

    path('inventario/', views.inventario, name = 'inventario'), 
    path('inventario/crear', views.crear_inventario, name = 'crear_inventario'),
    path('inventario/editar', views.editar_inventario, name = 'editar_inventario'),
    path('inventario/eliminar/<int:id>', views.eliminar_inventario, name = 'eliminar_inventario'),

    path('procesos', views.procesos, name = 'procesos'),
    path('procesos/crear', views.crear_procesos, name = 'crear_procesos'),
    path('procesos/<int:proceso_id>/eliminar_documento/', views.eliminar_documento, name='eliminar_documento'),
    path('procesos/<int:id>/detalles/', views.obtener_detalles_proceso, name='detalles_proceso'),
    path('agregar_equipo/<int:equipo_id>/', views.agregar_equipo, name='agregar_equipo'),
    path('eliminar_equipo/<int:equipo_id>/', views.eliminar_equipo, name='eliminar_equipo'),
    path('procesos/<int:proceso_id>/quitar-equipo/<int:equipo_id>/', views.quitar_equipo, name='quitar_equipo'),
    path('procesos/<int:id>/editar/', views.editar_proceso, name='editar_proceso'),
    path('procesos/<int:id>/recibir-equipo/', views.recibir_equipo, name='recibir_equipo'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
