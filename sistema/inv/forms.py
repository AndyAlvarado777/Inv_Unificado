from django import forms
from .models import Usuario
from .models import Inventario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('nombre', 'correo', 'departamento', 'puesto', 'rol', 'estado')
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'puesto': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(choices=[(1, 'Administrador'), (2, 'Usuario'), (3, 'Invitado')], attrs={'class': 'form-select'}),
            'estado': forms.Select(choices=[(1, 'Activo'), (2, 'Bloqueado'), (3, 'En espera')], attrs={'class': 'form-select'})
        }

class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ('tipo_equipo', 'serie', 'marca', 'modelo', 'observaciones', 'estado')
        widgets = {
            'tipo_equipo': forms.Select(choices=[(1, 'Equipo'), (2, 'Inventario')], attrs={'class': 'form-select'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'marca': forms.TextInput(attrs={'class': 'form-control'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(choices=[(1, 'En inventario'), (2, 'Asignado'),(3, 'Prestado')], attrs={'class': 'form-select'})
        }