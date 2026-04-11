from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from ..models import Estudiante, Matricula, Curso
from ..forms import EstudianteForm, MatriculaForm

# Estudiantes (Filtrado: solo los matriculados en cursos del usuario)
class EstudianteListView(LoginRequiredMixin, ListView):
    model = Estudiante
    template_name = 'grades/students/estudiante_list.html'
    context_object_name = 'estudiantes'

    def get_queryset(self):
        mis_cursos = Curso.objects.filter(docente=self.request.user)
        ids = Matricula.objects.filter(curso__in=mis_cursos).values_list('estudiante_id', flat=True)
        return Estudiante.objects.filter(pk__in=ids)

class EstudianteCreateView(LoginRequiredMixin, CreateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = 'grades/students/estudiante_form.html'
    success_url = reverse_lazy('estudiante_list')

class EstudianteUpdateView(LoginRequiredMixin, UpdateView):
    model = Estudiante
    form_class = EstudianteForm
    template_name = 'grades/students/estudiante_form.html'
    success_url = reverse_lazy('estudiante_list')

class EstudianteDeleteView(LoginRequiredMixin, DeleteView):
    model = Estudiante
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('estudiante_list')

# Matriculas (Filtrado por cursos del usuario)
class MatriculaListView(LoginRequiredMixin, ListView):
    model = Matricula
    template_name = 'grades/students/matricula_list.html'
    context_object_name = 'matriculas'

    def get_queryset(self):
        return Matricula.objects.filter(curso__docente=self.request.user)

class MatriculaCreateView(LoginRequiredMixin, CreateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = 'grades/students/matricula_form.html'
    success_url = reverse_lazy('matricula_list')

class MatriculaUpdateView(LoginRequiredMixin, UpdateView):
    model = Matricula
    form_class = MatriculaForm
    template_name = 'grades/students/matricula_form.html'
    success_url = reverse_lazy('matricula_list')

class MatriculaDeleteView(LoginRequiredMixin, DeleteView):
    model = Matricula
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('matricula_list')


@method_decorator(csrf_exempt, name='dispatch')
class CargaMasivaEstudiantesView(LoginRequiredMixin, View):
    """Carga masiva: recibe texto con nombres (uno por línea) y crea + matricula."""
    def post(self, request):
        try:
            data = json.loads(request.body)
            curso_id = data.get('curso_id')
            estudiantes = data.get('estudiantes', []) # Recibe lista de objetos {apellidos, nombres}

            curso = Curso.objects.get(pk=curso_id)
            creados = 0

            for entry in estudiantes:
                apellidos = entry.get('apellidos', '').strip()
                nombres = entry.get('nombres', '').strip()
                
                if not apellidos: continue

                # Crear estudiante
                estudiante = Estudiante.objects.create(
                    apellidos=apellidos,
                    nombres=nombres
                )
                # Matricular
                Matricula.objects.create(
                    estudiante=estudiante,
                    curso=curso
                )
                creados += 1

            return JsonResponse({'ok': True, 'creados': creados})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)
