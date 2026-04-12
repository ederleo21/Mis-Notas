from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.http import JsonResponse
from django.contrib import messages
from ..models import PeriodoLectivo, Nivel, Curso, Subject, Actividad
from ..forms import PeriodoForm, NivelForm, CursoForm, SubjectForm, ActividadForm

# Mixin para manejar errores de protección
class ProtectedDeleteMixin:
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            error_message = "No se puede eliminar este registro porque tiene datos asociados (ej: cursos, notas o alumnos)."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_message}, status=400)
            messages.error(request, error_message)
            return self.get(request, *args, **kwargs)

# Periodos
class PeriodoListView(LoginRequiredMixin, ListView):
    model = PeriodoLectivo
    template_name = 'grades/academic/periodo_list.html'
    context_object_name = 'periodos'

    def get_queryset(self):
        return PeriodoLectivo.objects.filter(docente=self.request.user)

class PeriodoCreateView(LoginRequiredMixin, CreateView):
    model = PeriodoLectivo
    form_class = PeriodoForm
    template_name = 'grades/academic/periodo_form.html'
    success_url = reverse_lazy('periodo_list')

    def form_valid(self, form):
        form.instance.docente = self.request.user
        return super().form_valid(form)

class PeriodoUpdateView(LoginRequiredMixin, UpdateView):
    model = PeriodoLectivo
    form_class = PeriodoForm
    template_name = 'grades/academic/periodo_form.html'
    success_url = reverse_lazy('periodo_list')

    def get_queryset(self):
        return PeriodoLectivo.objects.filter(docente=self.request.user)

class PeriodoDeleteView(LoginRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = PeriodoLectivo
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('periodo_list')

    def get_queryset(self):
        return PeriodoLectivo.objects.filter(docente=self.request.user)


# Niveles
class NivelListView(LoginRequiredMixin, ListView):
    model = Nivel
    template_name = 'grades/academic/nivel_list.html'
    context_object_name = 'niveles'

    def get_queryset(self):
        return Nivel.objects.filter(docente=self.request.user)

class NivelCreateView(LoginRequiredMixin, CreateView):
    model = Nivel
    form_class = NivelForm
    template_name = 'grades/academic/nivel_form.html'
    success_url = reverse_lazy('nivel_list')

    def form_valid(self, form):
        form.instance.docente = self.request.user
        return super().form_valid(form)

class NivelUpdateView(LoginRequiredMixin, UpdateView):
    model = Nivel
    form_class = NivelForm
    template_name = 'grades/academic/nivel_form.html'
    success_url = reverse_lazy('nivel_list')

    def get_queryset(self):
        return Nivel.objects.filter(docente=self.request.user)

class NivelDeleteView(LoginRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Nivel
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('nivel_list')

    def get_queryset(self):
        return Nivel.objects.filter(docente=self.request.user)

# Cursos (Filtrado por docente = usuario logueado)
class CursoListView(LoginRequiredMixin, ListView):
    model = Curso
    template_name = 'grades/academic/curso_list.html'
    context_object_name = 'cursos'

    def get_queryset(self):
        return Curso.objects.filter(docente=self.request.user)

class CursoCreateView(LoginRequiredMixin, CreateView):
    model = Curso
    form_class = CursoForm
    template_name = 'grades/academic/curso_form.html'
    success_url = reverse_lazy('curso_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.docente = self.request.user
        return super().form_valid(form)

class CursoUpdateView(LoginRequiredMixin, UpdateView):
    model = Curso
    form_class = CursoForm
    template_name = 'grades/academic/curso_form.html'
    success_url = reverse_lazy('curso_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        return Curso.objects.filter(docente=self.request.user)

class CursoDeleteView(LoginRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Curso
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('curso_list')

    def get_queryset(self):
        return Curso.objects.filter(docente=self.request.user)


# Materias (Subjects)
class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'grades/academic/subject_list.html'
    context_object_name = 'subjects'
    ordering = ['nombre']

class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'grades/academic/subject_form.html'
    success_url = reverse_lazy('subject_list')

class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = 'grades/academic/subject_form.html'
    success_url = reverse_lazy('subject_list')

class SubjectDeleteView(LoginRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Subject
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('subject_list')


# Actividades (Catalog)
class ActividadListView(LoginRequiredMixin, ListView):
    model = Actividad
    template_name = 'grades/academic/actividad_list.html'
    context_object_name = 'actividades'
    ordering = ['nombre']

class ActividadCreateView(LoginRequiredMixin, CreateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'grades/academic/actividad_form.html'
    success_url = reverse_lazy('actividad_list')

class ActividadUpdateView(LoginRequiredMixin, UpdateView):
    model = Actividad
    form_class = ActividadForm
    template_name = 'grades/academic/actividad_form.html'
    success_url = reverse_lazy('actividad_list')

class ActividadDeleteView(LoginRequiredMixin, ProtectedDeleteMixin, DeleteView):
    model = Actividad
    template_name = 'generic/confirm_delete.html'
    success_url = reverse_lazy('actividad_list')
