import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_sys.settings')
django.setup()

from grades.models import PeriodoLectivo, Nivel, Subject, TipoInsumo, Curso

def populate():
    print("Populating initial data...")
    
    # 1. Periodo Lectivo
    periodo, _ = PeriodoLectivo.objects.get_or_create(nombre="2024-2025", activo=True)
    print(f"- Periodo created: {periodo}")

    # 2. Niveles
    nivel, _ = Nivel.objects.get_or_create(nombre="3ero", paralelo="B")
    print(f"- Nivel created: {nivel}")

    # 3. Materias (from Excel)
    materias = [
        "Lengua y Literatura",
        "Matemática",
        "Ciencias Naturales",
        "Estudios Sociales",
        "Inglés",
        "Educación Cultural y Artística",
        "Educación Física",
        "Animación a la Lectura"
    ]
    for i, m_name in enumerate(materias):
        m, _ = Subject.objects.get_or_create(nombre=m_name, orden=i+1)
        print(f"  - Subject: {m}")

    # 4. Tipos de Insumos (from Excel)
    insumos = ["Tarea", "Activ. Individual", "Lección", "Evaluación"]
    for i_name in insumos:
        ti, _ = TipoInsumo.objects.get_or_create(nombre=i_name)
        print(f"  - TipoInsumo: {ti}")

    # 5. Curso (3ero B - 2024-2025)
    curso, _ = Curso.objects.get_or_create(periodo=periodo, nivel=nivel)
    print(f"- Curso created: {curso}")

    print("Success!")

if __name__ == "__main__":
    populate()
