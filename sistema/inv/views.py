from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Prefetch
from django.core.mail import EmailMessage
import openpyxl
from openpyxl.styles import Font
import os
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
import json
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.http import HttpResponse
from sistema import settings
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


#Vistas para el login y para loguearse 
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

@login_required
def eliminar_usuario(request, id):
    user = get_object_or_404(Usuario, id=id)
    # Verificar que no sea el propio usuario
    if request.user != user:
        user.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
    else:
        messages.error(request, 'No puedes eliminar tu propio usuario.')
    return redirect('usuarios')

@login_required
def editar_usuario(request, id):
    user = Usuario.objects.get(id=id)
    formulario = UsuarioForm(request.POST or None, instance=user)
    if formulario.is_valid() and request.POST:
        formulario.save()
        return redirect('usuarios')
    return render(request, 'usuarios/editar.html', {'formulario': formulario})

@login_required
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
@login_required
def inventario(request):
    inventario = Inventario.objects.all()
    # Aplicar filtros
    tipo_equipo = request.GET.get('tipo_equipo')
    estado = request.GET.get('estado')
    if tipo_equipo:
        inventario = inventario.filter(tipo_equipo=tipo_equipo)
    if estado:
        inventario = inventario.filter(estado=estado)
    context = {
        'inventario': inventario
    }
    return render(request, 'inventario/index.html', context)

@login_required
def crear_inventario(request):
    formulario = InventarioForm(request.POST or None)
    if formulario.is_valid():
        inventario = formulario.save(commit=False)
        inventario.save()
        return redirect('inventario')
    return render(request, 'inventario/crear.html', {'formulario': formulario})

@login_required
def editar_inventario(request):
    render(request, 'inventario/editar.html')

@login_required
def eliminar_inventario(request, id):
    inventario = get_object_or_404(Inventario, id=id)
    
    if inventario.detalles.exists():  # Verifica si hay relaciones en DetalleProceso
        return JsonResponse({'error': 'No se puede eliminar equipo asignado a un proceso'}, status=400)
    else:
        inventario.delete()
        return JsonResponse({'success': 'Equipo eliminado exitosamente'})


#---------------------------------------------------------------------------------------------
# Vistas para los procesos
@login_required
def procesos(request):
    procesos = Procesos.objects.all()
    return render(request, 'procesos/index.html', {'procesos': procesos})
    


@require_GET
def buscar_inventario(request):
    query = request.GET.get('buscar', '')
    inventario = Inventario.objects.filter(nombre__icontains=query).values('id', 'modelo')
    return JsonResponse(list(inventario), safe=False)
    
@login_required
def crear_procesos(request):
    if request.method == 'POST':
        form = ProcesoForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear proceso base
            proceso = form.save(commit=False)
            proceso.id_autorizo = 7
            proceso.id_autoriza_entrega = 7
            proceso.estado = 1
            if 'documento' in request.FILES:
                archivo = request.FILES['documento']
                fs = FileSystemStorage(location='C:/Temp')
                filename = fs.save(archivo.name, archivo)
                proceso.documento = f'C:/Temp/{filename}'
            proceso.save()  # Guardar primero para obtener ID[1][2]
            # Crear detalles del proceso y actualizar inventario
            equipos_seleccionados = request.POST.getlist('equipos')
            detalles_creados = []
            for equipo_id in equipos_seleccionados:
                equipo = Inventario.objects.get(id=equipo_id)
                detalle = DetalleProceso.objects.create(
                    proceso=proceso,
                    inventario=equipo
                )
                detalles_creados.append(detalle)
                equipo.estado = 2
                equipo.save()
            # Obtener datos frescos del proceso con relaciones[8]
            proceso_refreshed = Procesos.objects.prefetch_related('detalles').get(id=proceso.id)
            # Calcular y guardar la cantidad de días
            diferencia_dias = (proceso.fecha_fin - proceso.fecha_inicio).days
            proceso.cantidad_dias = diferencia_dias
            proceso.save()  # Guardar el cambio
            # Construir lista de equipos con detalles
            equipos_info = [
                f"{detalle.inventario.modelo} (Serie: {detalle.inventario.serie})"
                for detalle in proceso_refreshed.detalles.all()
            ]
            # Crear cuerpo del correo
            cuerpo = f"""
            Hola {proceso.solicitante.nombre} este correo es de parte del equipo de IT como prueba del proceso que se esta realizando,
            Préstamo registrado con éxito:
            **Equipos asignados:**
            {chr(10).join(['- ' + eq for eq in equipos_info])}
            
            **Detalles del préstamo:**
            - Fecha inicio: {proceso.fecha_inicio}
            - Fecha fin: {proceso.fecha_fin}
            - Ubicación: {proceso.ubicacion}
            """
            email = EmailMessage(
                subject=f"Nuevo préstamo {proceso.id}",
                body=cuerpo,
                from_email=settings.EMAIL_HOST_USER,
                to=[proceso.solicitante.correo],
                cc=[proceso.responsable.correo] if proceso.responsable else None
            ) 
            email.send()
            messages.success(request, 'Proceso creado y notificación enviada')
            return redirect('procesos')
        else:
            messages.error(request, 'Errores en el formulario')
            return render(request, 'procesos/crear.html', {'form': form})
    # GET request
    form = ProcesoForm()
    inventario = Inventario.objects.filter(estado=1)
    return render(request, 'procesos/crear.html', {'form': form, 'inventario': inventario})

@login_required
def eliminar_proceso(request, id):
    proceso = get_object_or_404(Procesos, id=id)
    # Actualizar estado de equipos antes de eliminar
    for detalle in proceso.detalles.all():
        equipo = detalle.inventario
        equipo.estado = 1  # 1 = 'En inventario'
        equipo.save(update_fields=['estado'])
    # Eliminar documento si existe
    if proceso.documento:
        archivo_path = proceso.documento.path
        if os.path.exists(archivo_path):
            os.remove(archivo_path)
    # Eliminar proceso y detalles (CASCADE automático)
    proceso.delete()
    messages.success(request, 'Proceso eliminado.')
    return redirect('procesos')

@login_required
def eliminar_documento(request, proceso_id):
    try:
        proceso = Procesos.objects.get(id=proceso_id)
        if proceso.documento:
            # Obtén el camino del archivo
            archivo_path = proceso.documento.path
            # Elimina el archivo del sistema de archivos
            if os.path.exists(archivo_path):
                os.remove(archivo_path)
            # Actualiza el campo documento a None
            proceso.documento = None
            proceso.save()
            messages.success(request, 'Documento eliminado correctamente.')
        else:
            messages.info(request, 'No hay documento asociado a este proceso.')
    except Procesos.DoesNotExist:
        messages.error(request, 'Proceso no encontrado.')
    return redirect('procesos')

@login_required
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
    
@login_required
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
    
@login_required
def editar_proceso(request, id):
    proceso = Procesos.objects.get(id=id)
    if request.method == 'POST':
        form = ProcesoForm(request.POST, request.FILES, instance=proceso)
        if form.is_valid():
            proceso = form.save(commit=False)  # No guardar inmediatamente
            # Manejar el archivo subido
            archivo = request.FILES.get('documento')
            if archivo:
                fs = FileSystemStorage(location='C:/Temp')
                filename = fs.save(archivo.name, archivo)
                proceso.documento = f'C:/Temp/{filename}'
            proceso.save()
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

@login_required
def recibir_equipo(request, id):
    if request.method == 'POST':
        fecha_regreso = request.POST.get('fecha_regreso')
        try:
            proceso = Procesos.objects.get(id=id)
            proceso.fecha_regreso = fecha_regreso
            proceso.estado = 2  # Estado regresado
            proceso.save()
            # Actualizar estado de los equipos relacionados
            for detalle in proceso.detalles.all():
                equipo = detalle.inventario
                equipo.estado = 1  # Estado en inventario
                equipo.save()
            messages.success(request, 'Equipo recibido con éxito.')
            return redirect('procesos')
        except Procesos.DoesNotExist:
            messages.error(request, 'Proceso no encontrado.')
            return redirect('procesos')
    else:
        return redirect('procesos')
    
    
@login_required
def agregar_equipo(request, equipo_id):
    if request.method == "POST":
        # Cambiar el estado del equipo a 4
        equipo = Inventario.objects.get(id=equipo_id)
        equipo.estado = 4
        equipo.save()
        return redirect('crear_procesos') 
    
@login_required
def eliminar_equipo(request, equipo_id):
    if request.method == "POST":
        equipo = Inventario.objects.get(id=equipo_id)
        equipo.estado = 1  # Cambiar el estado a "3"
        equipo.save()
        return JsonResponse({'success': True})


@login_required
def exportar_inventario(request):
    # Crear el libro de Excel y la hoja
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Inventario"
    # Definir los encabezados
    encabezados = ['ID', 'Tipo', 'Serie', 'Marca', 'Modelo', 'Observaciones', 'Estado']
    ws.append(encabezados)
    # Estilizar los encabezados
    header_font = Font(bold=True)
    for col in range(1, len(encabezados) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
    # Obtener los datos del inventario
    inventario = Inventario.objects.all()
    # Aplicar filtros
    tipo_equipo = request.GET.get('tipo_equipo')
    estado = request.GET.get('estado')
    if tipo_equipo:
        inventario = inventario.filter(tipo_equipo=tipo_equipo)
    if estado:
        inventario = inventario.filter(estado=estado)
    # Llenar la hoja con los datos
    for item in inventario:
        tipo = "Equipo" if item.tipo_equipo == 1 else "Inventario"
        estado = ""
        if item.estado == 1:
            estado = "En Inventario"
        elif item.estado == 2:
            estado = "Asignado"
        elif item.estado == 3:
            estado = "Prestado"
        elif item.estado == 4:
            estado = "En espera"
        fila = [item.id, tipo, item.serie, item.marca, item.modelo, item.observaciones, estado]
        ws.append(fila)
    # Ajustar el ancho de las columnas automáticamente
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter  # Obtener la letra de la columna
        for cell in col:
            try:  # Puede haber celdas sin valor
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)  # Agregar un poco de espacio
        ws.column_dimensions[column].width = adjusted_width
    # Preparar la respuesta HTTP
    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename="inventario.xlsx"'
    # Guardar el libro de Excel en la respuesta
    wb.save(response)
    return response

def asignacionEquipo(request):
    return render(request, 'asignacionEquipos/index.html')