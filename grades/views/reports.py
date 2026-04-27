from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from ..models import Curso, Subject, Matricula, Nota, Comportamiento, CursoActividad, _trunc2
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
            try:
                curso = Curso.objects.get(pk=curso_id)
            except Curso.DoesNotExist:
                return context

            subjects = list(curso.subjects.all().order_by('nombre'))
            subjects_count = len(subjects)
            matriculas = list(Matricula.objects.filter(curso=curso).select_related('estudiante').order_by('estudiante__apellidos', 'estudiante__nombres'))

            if not matriculas:
                context['show_table'] = True
                context['tabla'] = []
                context['subjects_list'] = subjects
                context['curso_sel'] = curso
                return context

            materia_sel = None
            if materia_id:
                materia_sel = next((s for s in subjects if str(s.pk) == str(materia_id)), None)

            # ── BULK PREFETCH: todas las CursoActividades del curso (3 trimestres) ──
            all_ca = list(CursoActividad.objects.filter(curso=curso))
            
            # Insumos por (subject_id, trimestre) → count
            insumos_count = {}
            for ca in all_ca:
                if ca.subject_id:
                    key = (ca.subject_id, ca.trimestre)
                    insumos_count[key] = insumos_count.get(key, 0) + 1

            # ── BULK PREFETCH: TODAS las notas del curso (todos trimestres, todas materias) ──
            mat_ids = [m.pk for m in matriculas]
            all_ca_ids = [ca.pk for ca in all_ca]
            
            all_notas = Nota.objects.filter(
                matricula_id__in=mat_ids,
                curso_actividad_id__in=all_ca_ids
            )
            
            # Diccionario: (matricula_id, subject_id, trimestre) → suma de valores
            notas_sum = {}
            for n in all_notas:
                key = (n.matricula_id, n.subject_id, n.trimestre)
                notas_sum[key] = notas_sum.get(key, 0) + float(n.valor)

            # ── BULK PREFETCH: comportamientos finales (trimestre=4) ──
            all_comps = Comportamiento.objects.filter(
                matricula_id__in=mat_ids,
                trimestre=4
            )
            comps_map = {c.matricula_id: c for c in all_comps}

            # ── Función helper: promedio de materia en un trimestre (sin queries) ──
            def calc_subject_avg(mat_id, subject_id, trimestre):
                count = insumos_count.get((subject_id, trimestre), 0)
                if count == 0:
                    return 0.0
                suma = notas_sum.get((mat_id, subject_id, trimestre), 0)
                return _trunc2(suma / count)

            # ── CONSTRUIR TABLA (sin queries adicionales) ──
            tabla = []
            for mat in matriculas:
                student_report = {
                    'matricula': mat,
                    'is_materia_view': bool(materia_sel),
                    'total_general': 0,
                    'promedio_general': 0,
                    'comportamiento_fin': comps_map.get(mat.pk)
                }
                
                subjects_to_process = [materia_sel] if materia_sel else subjects
                
                details = []
                for s in subjects_to_process:
                    t1 = calc_subject_avg(mat.pk, s.pk, 1)
                    t2 = calc_subject_avg(mat.pk, s.pk, 2)
                    t3 = calc_subject_avg(mat.pk, s.pk, 3)
                    pf = _trunc2((t1 + t2 + t3) / 3)
                        
                    details.append({
                        'subject': s, 't1': t1, 't2': t2, 't3': t3, 'prom_final': pf
                    })

                # Calculate totals using ALL subjects (even in single-materia view)
                if not materia_sel:
                    suma_finales = _trunc2(sum(d['prom_final'] for d in details))
                else:
                    # Calcular promedios finales de TODAS las materias sin queries
                    all_finals = []
                    for s in subjects:
                        st1 = calc_subject_avg(mat.pk, s.pk, 1)
                        st2 = calc_subject_avg(mat.pk, s.pk, 2)
                        st3 = calc_subject_avg(mat.pk, s.pk, 3)
                        all_finals.append(_trunc2((st1 + st2 + st3) / 3))
                    suma_finales = _trunc2(sum(all_finals))

                student_report['materias'] = details
                student_report['total_general'] = suma_finales
                student_report['promedio_general'] = _trunc2(suma_finales / subjects_count) if subjects_count > 0 else 0
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
