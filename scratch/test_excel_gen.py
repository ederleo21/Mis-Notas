import os
import django
import sys

# Setup django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_sys.settings')
django.setup()

from grades.utils.excel_reports import generar_excel_trimestre
from grades.models import Curso

def test():
    curso = Curso.objects.first()
    if not curso:
        print("No courses found.")
        return

    print(f"Testing for course: {curso}")
    
    # Detailed
    print("Generating Detailed Report...")
    wb_det = generar_excel_trimestre(curso.id, 1, resumido=False)
    wb_det.save("test_detailed.xlsx")
    print("Detailed Report saved to test_detailed.xlsx")
    
    # Summarized
    print("Generating Summarized Report...")
    wb_res = generar_excel_trimestre(curso.id, 1, resumido=True)
    wb_res.save("test_summarized.xlsx")
    print("Summarized Report saved to test_summarized.xlsx")

if __name__ == "__main__":
    test()
