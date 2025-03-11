from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
import json
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Usuario
from .forms import UsuarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Inventario
from .forms import InventarioForm
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.db.models import Q



def inicio(request):
    return render(request, 'inicio.html')


#Vistas para usuarios

def usuarios(request):
    user = Usuario.objects.all()
    return render(request, 'usuarios/index.html', {'user': user})

def crear_usuario(request):
    formulario = UsuarioForm(request.POST or None)
    if formulario.is_valid():
        usuario = formulario.save(commit=False)
        usuario.password = make_password(request.POST.get('password'))
        usuario.save()
        return redirect('usuarios')
    return render(request, 'usuarios/crear.html', {'formulario': formulario})

@login_required
def eliminar_usuario(request, id):
    user = Usuario.objects.get(Usuario, id=id)
    user.delete()
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
    return render(request, 'procesos/index.html')


@require_GET
def buscar_inventario(request):
    query = request.GET.get('buscar', '')
    inventario = Inventario.objects.filter(nombre__icontains=query).values('id', 'modelo')
    return JsonResponse(list(inventario), safe=False)
    
def crear_procesos(request):
    inventario = Inventario.objects.filter(estado=1)  # Filtra solo estado=3
    return render(request, 'procesos/crear.html', {'inventario': inventario})

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


     