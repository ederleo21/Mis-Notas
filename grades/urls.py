from django.urls import path
from .views import dashboard, academic, students, grading, reports

urlpatterns = [
    path('', dashboard.DashboardView.as_view(), name='dashboard'),
    
    # Periodos
    path('periodos/', academic.PeriodoListView.as_view(), name='periodo_list'),
    path('periodos/nuevo/', academic.PeriodoCreateView.as_view(), name='periodo_create'),
    path('periodos/<int:pk>/editar/', academic.PeriodoUpdateView.as_view(), name='periodo_update'),
    path('periodos/<int:pk>/eliminar/', academic.PeriodoDeleteView.as_view(), name='periodo_delete'),
    
    # Niveles
    path('niveles/', academic.NivelListView.as_view(), name='nivel_list'),
    path('niveles/nuevo/', academic.NivelCreateView.as_view(), name='nivel_create'),
    path('niveles/<int:pk>/editar/', academic.NivelUpdateView.as_view(), name='nivel_update'),
    path('niveles/<int:pk>/eliminar/', academic.NivelDeleteView.as_view(), name='nivel_delete'),
    
    # Cursos
    path('cursos/', academic.CursoListView.as_view(), name='curso_list'),
    path('cursos/nuevo/', academic.CursoCreateView.as_view(), name='curso_create'),
    path('cursos/<int:pk>/editar/', academic.CursoUpdateView.as_view(), name='curso_update'),
    path('cursos/<int:pk>/eliminar/', academic.CursoDeleteView.as_view(), name='curso_delete'),
    
    # Materias
    path('materias/', academic.SubjectListView.as_view(), name='subject_list'),
    path('materias/nueva/', academic.SubjectCreateView.as_view(), name='subject_create'),
    path('materias/<int:pk>/editar/', academic.SubjectUpdateView.as_view(), name='subject_update'),
    path('materias/<int:pk>/eliminar/', academic.SubjectDeleteView.as_view(), name='subject_delete'),

    # Actividades (Catalog)
    path('actividades/', academic.ActividadListView.as_view(), name='actividad_list'),
    path('actividades/nueva/', academic.ActividadCreateView.as_view(), name='actividad_create'),
    path('actividades/<int:pk>/editar/', academic.ActividadUpdateView.as_view(), name='actividad_update'),
    path('actividades/<int:pk>/eliminar/', academic.ActividadDeleteView.as_view(), name='actividad_delete'),

    # Estudiantes
    path('estudiantes/', students.EstudianteListView.as_view(), name='estudiante_list'),
    path('estudiantes/nuevo/', students.EstudianteCreateView.as_view(), name='estudiante_create'),
    path('estudiantes/<int:pk>/editar/', students.EstudianteUpdateView.as_view(), name='estudiante_update'),
    path('estudiantes/<int:pk>/eliminar/', students.EstudianteDeleteView.as_view(), name='estudiante_delete'),

    # Matriculas
    path('matriculas/', students.MatriculaListView.as_view(), name='matricula_list'),
    path('matriculas/nueva/', students.MatriculaCreateView.as_view(), name='matricula_create'),
    path('matriculas/<int:pk>/editar/', students.MatriculaUpdateView.as_view(), name='matricula_update'),
    path('matriculas/<int:pk>/eliminar/', students.MatriculaDeleteView.as_view(), name='matricula_delete'),

    # Registro de Notas (Grading)
    path('notas/', grading.RegistroNotasView.as_view(), name='notas_registro'),
    path('notas/guardar/', grading.GuardarNotaView.as_view(), name='guardar_nota'),
    path('notas/agregar-insumo/', grading.AgregarInsumoView.as_view(), name='agregar_insumo'),
    path('notas/carga-masiva/', students.CargaMasivaEstudiantesView.as_view(), name='carga_masiva'),
    path('notas/guardar-comportamiento/', grading.GuardarComportamientoView.as_view(), name='guardar_comportamiento'),
    path('notas/asignar-insumos-base/', grading.AsignarInsumosBaseView.as_view(), name='asignar_insumos_base'),
    path('notas/materias-por-curso/', grading.GetMateriasPorCursoView.as_view(), name='get_materias_por_curso'),
    path('notas/eliminar-insumo/', grading.EliminarInsumoView.as_view(), name='eliminar_insumo'),
    path('notas/editar-insumo/', grading.EditarInsumoView.as_view(), name='editar_insumo'),
    path('notas/reordenar-insumo/', grading.ReordenarInsumoView.as_view(), name='reordenar_insumo'),
    path('notas/eliminar-matricula/', grading.EliminarMatriculaView.as_view(), name='eliminar_matricula'),
    path('notas/editar-estudiante/', grading.EditarEstudianteView.as_view(), name='editar_estudiante'),

    # Reportes
    path('notas/anual/', reports.CuadroAnualView.as_view(), name='cuadro_anual'),
    path('notas/exportar-trimestre/', reports.ExportarTrimestreExcelView.as_view(), name='exportar_trimestre_excel'),
    path('notas/exportar-anual/', reports.ExportarAnualExcelView.as_view(), name='exportar_anual_excel'),
    path('notas/exportar-boletines/', reports.ExportarBoletinesExcelView.as_view(), name='exportar_boletines_excel'),
]
