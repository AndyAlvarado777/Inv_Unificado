from django import forms
from .models import Procesos, Usuario
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


class ProcesoForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ('solicitante', 'responsable', 'ubicacion', 'tipo', 
                 'fecha_inicio', 'fecha_fin', 'descripcion','documento')
        widgets = {
            'solicitante': forms.Select(attrs={'class': 'form-select'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(choices=[('prestamo', 'Préstamo'), ('entrega', 'Entrega')], 
                                attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Fecha de inicio'}
            ),
            'fecha_fin': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Fecha de fin'}
            ),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'documento': forms.FileInput(attrs={'class': 'form-control'}),  
        }

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Procesos
        fields = ('documento',)        

class RecibirEquipoForm(forms.Form):
    fecha_regreso = forms.DateField(label='Fecha de Regreso', widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha_regreso'].required = True
