from django.contrib import admin
from .models import Estudiante, Curso, Subject, PeriodoLectivo, Nivel, Matricula, Actividad, Nota

admin.site.register(Estudiante)
admin.site.register(Curso)
admin.site.register(Subject)
admin.site.register(PeriodoLectivo)
admin.site.register(Nivel)
admin.site.register(Matricula)
admin.site.register(Actividad)
admin.site.register(Nota)
