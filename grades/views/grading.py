from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from ..models import Curso, Subject, Actividad, Matricula, CursoActividad, Nota, Comportamiento, _trunc2
from ..forms import ActividadForm

class RegistroNotasView(LoginRequiredMixin, TemplateView):
    """Vista principal del módulo de registro de notas."""
    template_name = 'grades/grading/notas_registro.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cursos'] = Curso.objects.filter(docente=self.request.user).select_related('nivel', 'periodo', 'docente')
        
        curso_id = self.request.GET.get('curso', '')
        if curso_id:
            try:
                curso = Curso.objects.get(pk=curso_id)
                context['materias'] = curso.subjects.all().order_by('nombre')
            except Curso.DoesNotExist:
                context['materias'] = Subject.objects.none()
        else:
            context['materias'] = Subject.objects.none()
            
        context['trimestres'] = [
            {'value': 1, 'label': 'Primer Trimestre'},
            {'value': 2, 'label': 'Segundo Trimestre'},
            {'value': 3, 'label': 'Tercer Trimestre'},
        ]

        trimestre_val = self.request.GET.get('trimestre', '')
        materia_id = self.request.GET.get('materia', '')

        context['curso_sel_id'] = curso_id
        context['trimestre_sel_val'] = trimestre_val
        context['materia_sel_id'] = materia_id
        context['catalogo_actividades'] = Actividad.objects.all()

        if curso_id and trimestre_val and materia_id:
            try:
                curso = Curso.objects.get(pk=curso_id)
                materia = Subject.objects.get(pk=materia_id)
                trimestre = int(trimestre_val)
                # Seteamos de una vez estos valores para que los badges siempre salgan
                context['curso_sel'] = curso
                context['trimestre_sel'] = trimestre
                context['materia_sel'] = materia
            except (Curso.DoesNotExist, Subject.DoesNotExist, ValueError):
                return context

            matriculas = list(Matricula.objects.filter(curso=curso).select_related('estudiante').order_by('estudiante__apellidos', 'estudiante__nombres'))
            
            # Si no hay matriculados, no hay nada que procesar
            if not matriculas:
                context['show_table'] = True
                context['tabla'] = []
                context['curso_actividades'] = []
                return context

            curso_actividades = list(CursoActividad.objects.filter(
                curso=curso, 
                trimestre=trimestre, 
                subject=materia
            ).select_related('actividad').order_by('orden', 'pk'))

            # ── BULK PREFETCH: 1 query para TODAS las notas de este trimestre/materia ──
            mat_ids = [m.pk for m in matriculas]
            ca_ids = [ca.pk for ca in curso_actividades]
            
            all_notas = Nota.objects.filter(
                matricula_id__in=mat_ids,
                curso_actividad_id__in=ca_ids,
                subject=materia,
                trimestre=trimestre
            ).select_related('curso_actividad')
            
            # Diccionario: (matricula_id, curso_actividad_id) → nota
            notas_map = {}
            for n in all_notas:
                notas_map[(n.matricula_id, n.curso_actividad_id)] = n

            # ── BULK PREFETCH: 1 query para TODOS los comportamientos ──
            all_comps = Comportamiento.objects.filter(
                matricula_id__in=mat_ids,
                trimestre=trimestre
            )
            comps_map = {c.matricula_id: c for c in all_comps}

            # ── BULK PREFETCH: datos para total/promedio trimestral ──
            # Obtener TODAS las actividades del trimestre (todas las materias)
            all_ca_trim = list(CursoActividad.objects.filter(
                curso=curso,
                trimestre=trimestre
            ).select_related('actividad'))
            
            # Materias activas en este trimestre
            active_subject_ids_trim = list(set(ca.subject_id for ca in all_ca_trim if ca.subject_id))
            
            # TODAS las notas del trimestre (todas las materias) para los alumnos
            all_ca_trim_ids = [ca.pk for ca in all_ca_trim]
            all_notas_trim = Nota.objects.filter(
                matricula_id__in=mat_ids,
                curso_actividad_id__in=all_ca_trim_ids
            )
            
            # Diccionario: (matricula_id, subject_id) → [notas]
            notas_por_materia = {}
            for n in all_notas_trim:
                key = (n.matricula_id, n.subject_id)
                notas_por_materia.setdefault(key, []).append(float(n.valor))
            
            # Insumos por materia: subject_id → count de CursoActividades
            insumos_por_materia = {}
            for ca in all_ca_trim:
                if ca.subject_id:
                    insumos_por_materia[ca.subject_id] = insumos_por_materia.get(ca.subject_id, 0) + 1

            # ── CONSTRUIR TABLA (sin queries adicionales) ──
            num_insumos = len(curso_actividades)
            tabla = []
            for mat in matriculas:
                fila = {'matricula': mat, 'notas': [], 'promedio': 0}
                total = 0
                for ca in curso_actividades:
                    nota_obj = notas_map.get((mat.pk, ca.pk))
                    valor = float(nota_obj.valor) if nota_obj else ''
                    fila['notas'].append({
                        'actividad_id': ca.actividad.pk,
                        'through_id': ca.pk,
                        'matricula_id': mat.pk,
                        'valor': valor,
                    })
                    if nota_obj:
                        total += float(nota_obj.valor)
                
                fila['promedio'] = _trunc2(total / num_insumos) if num_insumos > 0 else 0
                fila['comportamiento_trim'] = comps_map.get(mat.pk)
                
                # Calcular total y promedio trimestral en Python (sin queries)
                trim_total = 0
                for sid in active_subject_ids_trim:
                    count = insumos_por_materia.get(sid, 0)
                    if count > 0:
                        suma = sum(notas_por_materia.get((mat.pk, sid), []))
                        trim_total += _trunc2(suma / count)
                fila['total_trim'] = _trunc2(trim_total)
                
                n_active = len(active_subject_ids_trim)
                fila['promedio_trim'] = _trunc2(trim_total / n_active) if n_active > 0 else 0
                
                tabla.append(fila)

            context['tabla'] = tabla
            context['curso_actividades'] = curso_actividades
            context['show_table'] = True

        return context


@method_decorator(csrf_exempt, name='dispatch')
class GuardarNotaView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            matricula_id = data.get('matricula_id')
            through_id = data.get('through_id')
            materia_id = data.get('materia_id')
            trimestre = data.get('trimestre')
            valor_raw = data.get('valor')
            
            try:
                valor = float(valor_raw) if (valor_raw != '' and valor_raw is not None) else 0.00
                if valor > 10: valor = 10.0
                elif valor < 0: valor = 0.0
            except (ValueError, TypeError):
                valor = 0.00
            
            lookup_ca = None if (through_id == 0 or through_id == '0') else through_id

            nota, created = Nota.objects.update_or_create(
                matricula_id=matricula_id,
                curso_actividad_id=lookup_ca, 
                subject_id=materia_id if materia_id else None,
                trimestre=trimestre,
                defaults={'valor': valor}
            )

            matricula = nota.matricula
            materia = nota.subject
            
            if trimestre != 4 and trimestre != '4':
                through_ids = CursoActividad.objects.filter(
                    curso=matricula.curso, 
                    trimestre=trimestre, 
                    subject=materia
                ).values_list('id', flat=True)
            else:
                return JsonResponse({
                    'ok': True,
                    'total_anual': float(matricula.get_anual_total()),
                    'promedio_anual': float(matricula.get_anual_average())
                })
            
            notas_qs = Nota.objects.filter(matricula=matricula, curso_actividad_id__in=through_ids)
            total = sum(float(n.valor) for n in notas_qs)
            count = len(through_ids)
            promedio = _trunc2(total / count) if count > 0 else 0

            return JsonResponse({
                'ok': True,
                'promedio': promedio,
                'total_trim': matricula.get_trimestre_total(trimestre),
                'promedio_trim': matricula.get_trimestre_average(trimestre)
            })
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AgregarInsumoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            curso_id = data.get('curso_id')
            actividad_id = data.get('actividad_id')
            materia_id = data.get('materia_id')
            trimestre = data.get('trimestre', 1)

            curso = Curso.objects.get(pk=curso_id)
            actividad = Actividad.objects.get(pk=actividad_id)
            
            ultimo = CursoActividad.objects.filter(curso=curso, trimestre=trimestre, subject_id=materia_id).order_by('-orden').first()
            siguiente_orden = (ultimo.orden + 1) if ultimo else 1

            CursoActividad.objects.create(
                curso=curso, 
                actividad=actividad,
                trimestre=trimestre,
                subject_id=materia_id,
                orden=siguiente_orden
            )
            return JsonResponse({'ok': True, 'actividad_id': actividad.pk, 'descripcion': actividad.nombre})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class GetMateriasPorCursoView(LoginRequiredMixin, View):
    def get(self, request):
        curso_id = request.GET.get('curso_id')
        try:
            curso = Curso.objects.get(pk=curso_id)
            materias = list(curso.subjects.all().order_by('nombre').values('id', 'nombre'))
            return JsonResponse({'ok': True, 'materias': materias})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class GuardarComportamientoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            matricula_id = data.get('matricula_id')
            trimestre = data.get('trimestre')
            valor = data.get('valor')

            comp, created = Comportamiento.objects.update_or_create(
                matricula_id=matricula_id,
                trimestre=trimestre,
                defaults={'valor': valor}
            )
            
            matricula = Matricula.objects.get(pk=matricula_id)
            return JsonResponse({
                'ok': True,
                'total_trim': matricula.get_trimestre_total(trimestre),
                'promedio_trim': matricula.get_trimestre_average(trimestre)
            })
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class EliminarInsumoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            through_id = data.get('through_id')
            CursoActividad.objects.filter(pk=through_id).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class EditarInsumoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            through_id = data.get('through_id')
            new_actividad_id = data.get('new_actividad_id')
            
            ca = CursoActividad.objects.get(pk=through_id)
            ca.actividad_id = new_actividad_id
            ca.save()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class EliminarMatriculaView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            Matricula.objects.filter(pk=data.get('matricula_id')).delete()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class EditarEstudianteView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            matricula = Matricula.objects.get(pk=data.get('matricula_id'))
            estudiante = matricula.estudiante
            estudiante.apellidos = data.get('apellidos')
            estudiante.nombres = data.get('nombres')
            estudiante.save()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class AsignarInsumosBaseView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            curso_id = data.get('curso_id')
            trimestre = data.get('trimestre', 1)
            actividades_ids = data.get('actividades_ids', [])

            curso = Curso.objects.get(pk=curso_id)
            materias = curso.subjects.all()

            assigned_count = 0
            for materia in materias:
                ultimo = CursoActividad.objects.filter(curso=curso, trimestre=trimestre, subject=materia).order_by('-orden').first()
                siguiente_orden = (ultimo.orden + 1) if ultimo else 1

                for act_id in actividades_ids:
                    actividad = Actividad.objects.get(pk=act_id)
                    exists = CursoActividad.objects.filter(curso=curso, subject=materia, trimestre=trimestre, actividad=actividad).exists()
                    if not exists:
                        CursoActividad.objects.create(curso=curso, subject=materia, actividad=actividad, trimestre=trimestre, orden=siguiente_orden)
                        siguiente_orden += 1
                        assigned_count += 1
            return JsonResponse({'ok': True, 'assigned': assigned_count})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class ReordenarInsumoView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            ca = CursoActividad.objects.get(pk=data.get('ca_id'))
            direction = data.get('direction')

            siblings = list(CursoActividad.objects.filter(curso=ca.curso, subject=ca.subject, trimestre=ca.trimestre).order_by('orden', 'pk'))
            idx = next((i for i, s in enumerate(siblings) if s.pk == ca.pk), None)

            if direction == 'left' and idx > 0:
                swap_with = siblings[idx - 1]
            elif direction == 'right' and idx < len(siblings) - 1:
                swap_with = siblings[idx + 1]
            else:
                return JsonResponse({'ok': True})

            ca.orden, swap_with.orden = swap_with.orden, ca.orden
            if ca.orden == swap_with.orden:
                ca.orden = idx - 1 if direction == 'left' else idx + 1
                swap_with.orden = idx
            ca.save()
            swap_with.save()
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)
