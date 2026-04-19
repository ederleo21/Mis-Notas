from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from ..models import Curso, Subject, Matricula, Nota, Comportamiento, _trunc2
from ..utils.excel_reports import generar_excel_trimestre, generar_excel_anual, generar_excel_boletines_individuales
import io

class CuadroAnualView(LoginRequiredMixin, TemplateView):
    """Vista del Cuadro Final editable que consolida los 3 trimestres."""
    template_name = 'grades/reports/cuadro_anual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.filter(docente=self.request.user).select_related('nivel', 'periodo')
        
        curso_id = self.request.GET.get('curso', '')
        materia_id = self.request.GET.get('materia', '')
        context['curso_sel_id'] = curso_id
        context['materia_sel_id'] = materia_id

        if curso_id:
            curso = Curso.objects.get(pk=curso_id)
            subjects = curso.subjects.all().order_by('nombre')
            matriculas = Matricula.objects.filter(curso=curso).select_related('estudiante').order_by('estudiante__apellidos', 'estudiante__nombres')

            materia_sel = None
            if materia_id:
                materia_sel = subjects.filter(pk=materia_id).first()

            tabla = []
            for mat in matriculas:
                student_report = {
                    'matricula': mat,
                    'is_materia_view': bool(materia_sel),
                    'total_general': 0,
                    'promedio_general': 0,
                    'comportamiento_fin': Comportamiento.objects.filter(matricula=mat, trimestre=4).first()
                }
                
                subjects_to_process = [materia_sel] if materia_sel else subjects
                
                details = []
                for s in subjects_to_process:
                    t1 = mat.get_subject_average(s, 1)
                    t2 = mat.get_subject_average(s, 2)
                    t3 = mat.get_subject_average(s, 3)
                    pf = _trunc2((t1 + t2 + t3) / 3)
                        
                    details.append({
                        'subject': s, 't1': t1, 't2': t2, 't3': t3, 'prom_final': pf
                    })

                # Calculate totals using ALL subjects (even in single-materia view)
                if not materia_sel:
                    suma_finales = _trunc2(sum(d['prom_final'] for d in details))
                else:
                    suma_finales = _trunc2(sum(mat.get_subject_final(s) for s in subjects))

                student_report['materias'] = details
                student_report['total_general'] = suma_finales
                student_report['promedio_general'] = _trunc2(suma_finales / subjects.count()) if subjects.exists() else 0
                tabla.append(student_report)

            context['curso_sel'] = curso
            context['subjects_list'] = subjects
            context['materia_sel'] = materia_sel
            context['tabla'] = tabla
            context['show_table'] = True
        return context


class ExportarTrimestreExcelView(LoginRequiredMixin, View):
    """Genera y descarga el Excel del trimestre para un curso."""
    def get(self, request):
        curso_id = request.GET.get('curso')
        trimestre = request.GET.get('trimestre')
        tipo = request.GET.get('tipo', 'detallado')
        resumido = (tipo == 'resumido')
        
        if not curso_id or not trimestre:
            return HttpResponse("Faltan parámetros", status=400)
            
        curso = Curso.objects.get(pk=curso_id)
        wb = generar_excel_trimestre(curso_id, int(trimestre), resumido=resumido)
        
        # Guardar en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Usar str(curso) para el nombre del archivo
        nombre_limpio = str(curso).replace(' ', '_').replace('-', '_')
        label = "Resumido" if resumido else "Trimestral"
        filename = f"Cuadro_{label}_{nombre_limpio}_T{trimestre}.xlsx"
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

class ExportarAnualExcelView(LoginRequiredMixin, View):
    """Genera y descarga el Excel de consolidado anual."""
    def get(self, request):
        curso_id = request.GET.get('curso')
        if not curso_id:
            return HttpResponse("Falta parámetro curso", status=400)
            
        curso = Curso.objects.get(pk=curso_id)
        wb = generar_excel_anual(curso_id)
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        nombre_limpio = str(curso).replace(' ', '_').replace('-', '_')
        filename = f"Cuadro_Anual_CONSOLIDADO_{nombre_limpio}.xlsx"
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

class ExportarBoletinesExcelView(LoginRequiredMixin, View):
    """Genera y descarga los boletines individuales de un curso."""
    def get(self, request):
        curso_id = request.GET.get('curso')
        if not curso_id:
            return HttpResponse("Falta parámetro curso", status=400)
            
        curso = Curso.objects.get(pk=curso_id)
        wb = generar_excel_boletines_individuales(curso_id)
        
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        nombre_limpio = str(curso).replace(' ', '_').replace('-', '_')
        filename = f"Boletines_Individuales_{nombre_limpio}.xlsx"
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
