from django.db import models

# Create your models here.
class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, verbose_name='Nombre', db_index=True)
    correo = models.CharField(max_length=100, verbose_name='Correo', db_index=True)
    departamento = models.CharField(max_length=100, verbose_name='Departamento', db_index=True)
    puesto = models.CharField(max_length=100, verbose_name='Puesto', db_index=True)
    ROL_CHOICES = [
        (1, 'Administrador'),
        (2, 'Usuario'),
        (3, 'Invitado')
    ]
    rol = models.IntegerField(verbose_name='rol', choices=ROL_CHOICES, db_index=True)
    password = models.CharField(max_length=100, verbose_name='Password', db_index=True)
    PASS_CHOICES = [
        (1, 'Administrador'),
        (2, 'Usuario'),
        (3, 'Invitado')
    ]
    estado = models.IntegerField(verbose_name='Estado', db_index=True)

    def __str__(self):
        return self.nombre  # Representación legible del usuario
    
class Inventario(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_equipo = models.IntegerField(verbose_name='Tipo Equipo', db_index=True)
    serie = models.CharField(max_length=100, verbose_name='Serie', db_index=True)
    marca = models.CharField(max_length=100,verbose_name='Marca', db_index=True)
    modelo = models.CharField(max_length=100,verbose_name='Modelo', db_index=True)
    observaciones = models.CharField(max_length=200,verbose_name='Observaciones', db_index=True)
    ESTADO_OPCIONES = (
        (1, 'En inventario'),
        (2, 'En préstamo'), 
        (3, 'En bodega'),  # Valor que nos interesa
    )
    estado = models.IntegerField(verbose_name='Estado', db_index=True)

    def __str__(self):
        return self.nombre  # Representación legible del usuario
    
class Procesos(models.Model):
    id = models.AutoField(primary_key=True)
    id_solicitante = models.IntegerField(verbose_name='Solicitante', db_index=True)    
    id_responsable = models.IntegerField(verbose_name='Responsable', db_index=True)
    id_autorizo = models.IntegerField(verbose_name='Autorizo', db_index=True)
    id_autoriza_entrega = models.IntegerField(verbose_name='Autoriza Entrega', db_index=True)
    fecha_inicio = models.DateField(verbose_name='Fecha Inicio', db_index=True)
    fecha_fin = models.DateField(verbose_name='Fecha Fin', db_index=True)
    fecha_regreso = models.DateField(verbose_name='Fecha Regreso', db_index=True)
    estado = models.IntegerField(verbose_name='Estado', db_index=True)

    
class DetalleProceso(models.Model):
    id = models.AutoField(primary_key=True)
    id_proceso = models.IntegerField(verbose_name='Proceso', db_index=True)
    id_inventario = models.IntegerField(verbose_name='Inventario', db_index=True)
    
    


