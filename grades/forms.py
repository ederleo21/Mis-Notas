from django import forms
from django.contrib.auth import get_user_model
from .models import PeriodoLectivo, Curso, Estudiante, Nivel, Matricula, Subject, Actividad

User = get_user_model()

class PeriodoForm(forms.ModelForm):
    class Meta:
        model = PeriodoLectivo
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 2024-2025'}),
        }

class NivelForm(forms.ModelForm):
    class Meta:
        model = Nivel
        fields = ['nombre', 'paralelo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: 3ero'}),
            'paralelo': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: B'}),
        }

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['periodo', 'nivel', 'subjects']
        widgets = {
            'periodo': forms.Select(attrs={'class': 'form-input'}),
            'nivel': forms.Select(attrs={'class': 'form-input'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'form-input', 'size': 8}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['periodo'].queryset = PeriodoLectivo.objects.filter(docente=user)
            self.fields['nivel'].queryset = Nivel.objects.filter(docente=user)
            # subjects remains shared (all Subjects displayed)


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['apellidos', 'nombres']
        widgets = {
            'apellidos': forms.TextInput(attrs={'class': 'form-input'}),
            'nombres': forms.TextInput(attrs={'class': 'form-input'}),
        }

class MatriculaForm(forms.ModelForm):
    class Meta:
        model = Matricula
        fields = ['estudiante', 'curso']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-input'}),
            'curso': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['estudiante'].queryset = Estudiante.objects.filter(docente=user)
            self.fields['curso'].queryset = Curso.objects.filter(docente=user)

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Matemáticas'}),
        }


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ej: Tarea 1...'}),
        }
