from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Avg, Sum
import math

User = get_user_model()

def _trunc2(val):
    """Trunca a 2 decimales SIN redondear."""
    return math.trunc(float(val) * 100) / 100

TRIMESTRE_CHOICES = [
    (1, 'Primer Trimestre'),
    (2, 'Segundo Trimestre'),
    (3, 'Tercer Trimestre'),
    (4, 'Anual / Final'),
]

class PeriodoLectivo(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Año Lectivo")
    docente = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="periodos")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Periodos Lectivos"

class Nivel(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Grado/Curso") 
    paralelo = models.CharField(max_length=5, verbose_name="Paralelo") 
    docente = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="niveles")
    def __str__(self):
        return f"{self.nombre} {self.paralelo}"

    class Meta:
        verbose_name_plural = "Niveles"

class Curso(models.Model):
    periodo = models.ForeignKey(PeriodoLectivo, on_delete=models.PROTECT)
    nivel = models.ForeignKey(Nivel, on_delete=models.PROTECT)
    subjects = models.ManyToManyField('Subject', blank=True, related_name='cursos')
    actividades = models.ManyToManyField('Actividad', blank=True, related_name='cursos', through='CursoActividad')
    docente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="cursos")

    def __str__(self):
        return f"{self.nivel} - {self.periodo}"

class Subject(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Estudiante(models.Model):
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    docente = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="estudiantes")

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

class Matricula(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.estudiante} ({self.curso})"

    def get_subject_average(self, subject, trimestre):
        """Calcula el promedio de una materia en un trimestre específico (truncado a 2 decimales)."""
        from .models import CursoActividad
        # Filtrar los insumos específicos para esta materia y trimestre
        ca_list = CursoActividad.objects.filter(
            curso=self.curso, 
            subject=subject, 
            trimestre=trimestre
        )
        if not ca_list.exists():
            return 0.0
            
        # Obtener las notas vinculadas a esos insumos específicos
        notas = Nota.objects.filter(
            matricula=self,
            curso_actividad__in=ca_list
        )
        
        suma = (notas.aggregate(Sum('valor'))['valor__sum'] or 0)
        total_insumos = ca_list.count()
        
        return _trunc2(float(suma) / total_insumos) if total_insumos > 0 else 0.0

    def get_subject_final(self, subject):
        """Calcula la nota final de una materia: promedio de los 3 trimestres (truncado)."""
        # Solo promediamos trimestres donde la materia realmente tuvo actividad
        from .models import CursoActividad
        trimestres_activos = []
        for t in [1, 2, 3]:
            if CursoActividad.objects.filter(curso=self.curso, subject=subject, trimestre=t).exists():
                trimestres_activos.append(self.get_subject_average(subject, t))
        
        if not trimestres_activos:
            return 0.0
        return _trunc2(sum(trimestres_activos) / len(trimestres_activos))

    def get_anual_total(self):
        """Suma de los promedios finales de cada materia activa (que tenga al menos una actividad en el año)."""
        from .models import CursoActividad
        active_subject_ids = CursoActividad.objects.filter(
            curso=self.curso
        ).values_list('subject_id', flat=True).distinct()
        
        subjects = self.curso.subjects.filter(id__in=active_subject_ids)
        total = 0
        for s in subjects:
            total += self.get_subject_final(s)
        return _trunc2(total)

    def get_anual_average(self):
        """Promedio anual general basado solo en materias con actividades (truncado)."""
        from .models import CursoActividad
        active_subjects_count = CursoActividad.objects.filter(
            curso=self.curso
        ).values_list('subject_id', flat=True).distinct().count()
        
        if active_subjects_count > 0:
            return _trunc2(self.get_anual_total() / active_subjects_count)
        return 0.0

    def get_trimestre_total(self, trimestre):
        """Suma de promedios de materias que tienen actividades en este trimestre (truncado)."""
        from .models import CursoActividad
        active_subject_ids = CursoActividad.objects.filter(
            curso=self.curso,
            trimestre=trimestre
        ).values_list('subject_id', flat=True).distinct()
        
        subjects = self.curso.subjects.filter(id__in=active_subject_ids)
        return _trunc2(sum(self.get_subject_average(s, trimestre) for s in subjects))

    def get_trimestre_average(self, trimestre):
        """Promedio general del trimestre basado solo en materias activas (truncado)."""
        from .models import CursoActividad
        active_subjects_count = CursoActividad.objects.filter(
            curso=self.curso, 
            trimestre=trimestre
        ).values_list('subject_id', flat=True).distinct().count()
        
        if active_subjects_count > 0:
            return _trunc2(self.get_trimestre_total(trimestre) / active_subjects_count)
        return 0.0

    class Meta:
        ordering = ['estudiante__apellidos', 'estudiante__nombres']
        unique_together = ('curso', 'estudiante')

class Actividad(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Actividades"
        ordering = ['nombre']

class CursoActividad(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    actividad = models.ForeignKey(Actividad, on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, null=True, blank=True)
    orden = models.PositiveIntegerField(default=0)
    trimestre = models.PositiveSmallIntegerField(choices=TRIMESTRE_CHOICES, default=1)

    class Meta:
        ordering = ['orden', 'pk']
        verbose_name = "Actividad por Curso"
        verbose_name_plural = "Actividades por Curso"

class Nota(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    curso_actividad = models.ForeignKey(CursoActividad, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT)
    trimestre = models.PositiveIntegerField(choices=TRIMESTRE_CHOICES, default=1)
    valor = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        act_name = self.curso_actividad.actividad.nombre if self.curso_actividad else "Sin Asignar"
        return f"{self.matricula.estudiante} - {act_name} ({self.subject} T{self.trimestre}): {self.valor}"

class Comportamiento(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    trimestre = models.PositiveIntegerField(choices=TRIMESTRE_CHOICES)
    valor = models.CharField(max_length=1, choices=[('A','A'),('B','B'),('C','C'),('D','D'),('E','E')], default='B')

    def __str__(self):
        return f"Comportamiento {self.matricula.estudiante} - T{self.trimestre}: {self.valor}"
