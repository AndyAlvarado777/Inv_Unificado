from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.timezone import now
# Create your models here.


class UsuarioManager(BaseUserManager):
    def create_user(self, correo, password=None, **extra_fields):
        if not correo:
            raise ValueError('El correo es obligatorio')
        user = self.model(correo=self.normalize_email(correo), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(correo, password, **extra_fields)
class Usuario(AbstractBaseUser, PermissionsMixin):
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
    last_login = models.DateTimeField(verbose_name='Último inicio de sesión', default=now)
    PASS_CHOICES = [
        (1, 'Administrador'),
        (2, 'Usuario'),
        (3, 'Invitado')
    ]
    estado = models.IntegerField(verbose_name='Estado', db_index=True)
    is_staff = models.BooleanField(default=False)  # Obligatorio para admin
    is_active = models.BooleanField(default=True) 
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']
    
    objects = UsuarioManager()

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
    id = models.AutoField(primary_key=True, db_index=True)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitante', null=True, db_index=True)    
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='responsable', null=True, db_index=True)     
    id_autorizo = models.IntegerField(verbose_name='Autorizo', db_index=True)
    id_autoriza_entrega = models.IntegerField(verbose_name='Autoriza Entrega', db_index=True)
    fecha_inicio = models.DateField(verbose_name='Fecha Inicio', db_index=True)
    fecha_fin = models.DateField(verbose_name='Fecha Fin', db_index=True)
    fecha_regreso = models.DateField(verbose_name='Fecha Regreso', db_index=True, null=True)
    ubicacion = models.CharField(max_length=200, verbose_name='ubicacion', null=True)
    tipo = models.CharField(max_length=20, verbose_name='Tipo', null=True)
    descripcion = models.CharField(max_length=200, verbose_name='Descripción', null=True)
    estado = models.IntegerField(verbose_name='Estado', db_index=True)

    
class DetalleProceso(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    proceso = models.ForeignKey(Procesos, on_delete=models.CASCADE, related_name='detalles', null=True, db_index=True)
    inventario = models.ForeignKey(Inventario, on_delete=models.CASCADE, related_name='detalles', null=True, db_index=True)
    



