from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Prefetch

# Create your views here.
import json
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import DetalleProceso, Procesos, Usuario
from .forms import ProcesoForm, UsuarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Inventario
from .forms import InventarioForm
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout
from django.contrib import messages


@login_required
def inicio(request):
    return render(request, 'inicio.html')

def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        try:
            # Autenticar al usuario
            user = authenticate(request, correo=correo, password=password)

            if user is not None:
                if user.estado == 1:  # Verificar si el estado del usuario es activo
                    auth_login(request, user)  # Iniciar sesión

                    # Redirigir según el rol del usuario
                    if user.rol == 1:  # Administrador
                        return redirect('inicio')
                    elif user.rol == 2:  # Usuario
                        messages.error(request, "Tu cuenta es Usuario. Aun no hay vista Usuario.")
                    elif user.rol == 3:  # Invitado
                        messages.error(request, "Tu cuenta es Invitado. Aun no hay vista Invitado.")
                else:
                    messages.error(request, "Tu cuenta está inactiva. Contacta al administrador.")
            else:
                messages.error(request, "Credenciales inválidas.")
        except MultipleObjectsReturned:
            # Contar cuántos usuarios tienen el mismo correo
            usuarios_con_correo = Usuario.objects.filter(correo=correo)
            cantidad = usuarios_con_correo.count()

            # Mostrar mensaje de error indicando el problema
            messages.error(
                request,
                f"Se encontraron {cantidad} usuarios con el mismo correo '{correo}'. Contacta al administrador."
            )

        return render(request, 'registration/login.html')

    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('inicio')  # Redirige a la página principal o a la página de login


#Vistas para usuarios
@login_required
def usuarios(request):
    user = Usuario.objects.all()
    return render(request, 'usuarios/index.html', {'user': user})

@login_required
def perfil(request):
    usuario_actual = request.user  # Usuario autenticado
    return render(request, 'usuarios/perfil.html', {'usuario': usuario_actual})

@login_required
def crear_usuario(request):
    formulario = UsuarioForm(request.POST or None)
    if formulario.is_valid():
        usuario = formulario.save(commit=False)
        usuario.password = make_password(request.POST.get('password'))
        usuario.save()
        return redirect('usuarios')
    return render(request, 'usuarios/crear.html', {'formulario': formulario})

def eliminar_usuario(request, id):
    user = get_object_or_404(Usuario, id=id)
    
    # Verificar que no sea el propio usuario
    if request.user != user:
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    else:
        messages.error(request, 'No puedes eliminar tu propio usuario.')

    return redirect('usuarios')

def editar_usuario(request, id):
    user = Usuario.objects.get(id=id)
    formulario = UsuarioForm(request.POST or None, instance=user)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('usuarios')
    return render(request, 'usuarios/editar.html', {'formulario': formulario})

@csrf_exempt  # Solo para pruebas; usa un middleware CSRF en producción.
def restablecer_contrasena(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_password = data.get('new_password')

            if not new_password:
                return JsonResponse({'error': 'La nueva contraseña es obligatoria.'}, status=400)

            user = Usuario.objects.get(id=id)
            user.password = make_password(new_password)  # Encripta la contraseña antes de guardarla.
            user.save()

            return JsonResponse({'message': 'Contraseña restablecida con éxito.'}, status=200)
        except Usuario.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos inválidos.'}, status=400)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)
    



# Vistas para Inventario.

def inventario(request):
    inventario = Inventario.objects.all()
    return render(request, 'inventario/index.html', {'inventario': inventario})
    

def crear_inventario(request):
    formulario = InventarioForm(request.POST or None)
    if formulario.is_valid():
        inventario = formulario.save(commit=False)
        inventario.save()
        return redirect('inventario')
    return render(request, 'inventario/crear.html', {'formulario': formulario})

def editar_inventario(request):
    render(request, 'inventario/editar.html')

def eliminar_inventario(request, id):
    inventario = get_object_or_404(Inventario,id=id)
    inventario.delete()
    return redirect('inventario')



# Vistas para los procesos

def procesos(request):
    procesos = Procesos.objects.all()
    return render(request, 'procesos/index.html', {'procesos': procesos})
    


@require_GET
def buscar_inventario(request):
    query = request.GET.get('buscar', '')
    inventario = Inventario.objects.filter(nombre__icontains=query).values('id', 'modelo')
    return JsonResponse(list(inventario), safe=False)
    

def crear_procesos(request):
    
    if request.method == 'POST':
        form = ProcesoForm(request.POST)
        equipos_seleccionados = request.POST.getlist('equipos')  # Obtener equipos seleccionados

        if form.is_valid():
            # Guardar el proceso principal
            proceso = form.save(commit=False)
            proceso.id_autorizo = 7  # Valor fijo
            proceso.id_autoriza_entrega = 7  # Valor fijo
            proceso.estado = 1  # Estado inicial
            proceso.save()

            # Crear detalles del proceso para cada equipo seleccionado
            equipos_seleccionados = request.POST.getlist('equipos')
            for equipo_id in equipos_seleccionados:
                equipo = Inventario.objects.get(id=equipo_id)  # Obtén la instancia
                DetalleProceso.objects.create(
                    proceso=proceso,
                    inventario=equipo
                )
                # Actualizar estado del equipo a inactivo
                Inventario.objects.filter(id=equipo_id).update(estado=2)

            messages.success(request, 'Proceso creado exitosamente!')
            return redirect('procesos')  # Redirigir a la lista de procesos
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')

    else:
        form = ProcesoForm()

    inventario = Inventario.objects.filter(estado=1)
    return render(request, 'procesos/crear.html', {'form': form, 'inventario': inventario})

def obtener_detalles_proceso(request, id):
    try:
        proceso = Procesos.objects.select_related(
            'solicitante', 
            'responsable'
        ).prefetch_related(
            Prefetch('detalles', queryset=DetalleProceso.objects.select_related('inventario'))
        ).get(id=id)
        
        detalles_equipos = []
        for detalle in proceso.detalles.all():
            equipo = detalle.inventario
            detalles_equipos.append({
                'id_equipo': equipo.id,
                'tipo_equipo': equipo.tipo_equipo,
                'serie': equipo.serie,
                'marca': equipo.marca,
                'modelo': equipo.modelo,
                'observaciones': equipo.observaciones
            })
        
        data = {
            'proceso': {
                'solicitante': f"{proceso.solicitante}",
                'responsable': f"{proceso.responsable}",
                'fecha_regreso': proceso.fecha_regreso.strftime('%d/%m/%Y') if proceso.fecha_regreso else 'N/A',
                'ubicacion': proceso.ubicacion,
                'tipo': proceso.tipo,
                'descripcion': proceso.descripcion
            },
            'equipos': detalles_equipos
        }
        return JsonResponse(data)
    
    except Procesos.DoesNotExist:
        return JsonResponse({'error': 'Proceso no encontrado'}, status=404)
    
def quitar_equipo(request, proceso_id, equipo_id):
    try:
        # Obtener el detalle del proceso
        detalle = DetalleProceso.objects.get(proceso_id=proceso_id, inventario_id=equipo_id)
        
        # Cambiar el estado del equipo a "1" (En inventario)
        Inventario.objects.filter(id=equipo_id).update(estado=1)
        
        # Eliminar la fila del detalle del proceso
        detalle.delete()
        
        return JsonResponse({'success': True})
    
    except DetalleProceso.DoesNotExist:
        return JsonResponse({'error': 'Equipo no encontrado en el proceso'}, status=404)
    

def editar_proceso(request, id):
    proceso = Procesos.objects.get(id=id)
    
    if request.method == 'POST':
        form = ProcesoForm(request.POST, instance=proceso)
        
        if form.is_valid():
            form.save()
            # Agregar lógica para agregar nuevos equipos al proceso
            equipos_seleccionados = request.POST.getlist('equipos')
            for equipo_id in equipos_seleccionados:
                equipo = Inventario.objects.get(id=equipo_id)
                DetalleProceso.objects.get_or_create(
                    proceso=proceso,
                    inventario=equipo
                )
                Inventario.objects.filter(id=equipo_id).update(estado=2)
            
            messages.success(request, 'Proceso editado exitosamente!')
            return redirect('procesos')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProcesoForm(instance=proceso)
        inventario = Inventario.objects.filter(estado=1)
    
    return render(request, 'procesos/editar.html', {'form': form, 'inventario': inventario})


def agregar_equipo(request, equipo_id):
    if request.method == "POST":
        # Cambiar el estado del equipo a 4
        equipo = Inventario.objects.get(id=equipo_id)
        equipo.estado = 4
        equipo.save()
        return redirect('crear_procesos') 
    
def eliminar_equipo(request, equipo_id):
    if request.method == "POST":
        equipo = Inventario.objects.get(id=equipo_id)
        equipo.estado = 1  # Cambiar el estado a "3"
        equipo.save()
        return JsonResponse({'success': True})


     