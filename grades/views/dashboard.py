from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import Estudiante, Curso, Subject, Matricula

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'grades/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mis_cursos = Curso.objects.filter(docente=self.request.user)
        context['num_cursos'] = mis_cursos.count()
        context['num_estudiantes'] = Matricula.objects.filter(curso__in=mis_cursos).values('estudiante').distinct().count()
        context['num_materias'] = Subject.objects.count()
        return context
