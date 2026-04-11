# Entry point for modular views
from .v_modules import dashboard, academic, students, grading, reports

# Expose views for backward compatibility and clean URL usage
DashboardView = dashboard.DashboardView

# Academic
PeriodoListView = academic.PeriodoListView
PeriodoCreateView = academic.PeriodoCreateView
PeriodoUpdateView = academic.PeriodoUpdateView
PeriodoDeleteView = academic.PeriodoDeleteView
NivelListView = academic.NivelListView
NivelCreateView = academic.NivelCreateView
NivelUpdateView = academic.NivelUpdateView
NivelDeleteView = academic.NivelDeleteView
CursoListView = academic.CursoListView
CursoCreateView = academic.CursoCreateView
SubjectListView = academic.SubjectListView
SubjectCreateView = academic.SubjectCreateView
ActividadListView = academic.ActividadListView
ActividadCreateView = academic.ActividadCreateView
ActividadUpdateView = academic.ActividadUpdateView
ActividadDeleteView = academic.ActividadDeleteView

# Students
EstudianteListView = students.EstudianteListView
EstudianteCreateView = students.EstudianteCreateView
MatriculaListView = students.MatriculaListView
MatriculaCreateView = students.MatriculaCreateView
CargaMasivaEstudiantesView = students.CargaMasivaEstudiantesView

# Grading
RegistroNotasView = grading.RegistroNotasView
GuardarNotaView = grading.GuardarNotaView
AgregarInsumoView = grading.AgregarInsumoView
GetMateriasPorCursoView = grading.GetMateriasPorCursoView
GuardarComportamientoView = grading.GuardarComportamientoView
EliminarInsumoView = grading.EliminarInsumoView
EditarInsumoView = grading.EditarInsumoView
EliminarMatriculaView = grading.EliminarMatriculaView
EditarEstudianteView = grading.EditarEstudianteView
AsignarInsumosBaseView = grading.AsignarInsumosBaseView
ReordenarInsumoView = grading.ReordenarInsumoView

# Reports
CuadroAnualView = reports.CuadroAnualView
