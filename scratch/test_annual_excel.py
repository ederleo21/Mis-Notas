import os
import django
import sys

# Setup django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_sys.settings')
django.setup()

from grades.utils.excel_reports import generar_excel_anual
from grades.models import Curso

def test():
    curso = Curso.objects.first()
    if not curso:
        print("No courses found.")
        return

    print(f"Testing Annual Report for course: {curso}")
    
    try:
        wb = generar_excel_anual(curso.id)
        wb.save("test_annual_concentrated.xlsx")
        print("Annual Report saved to test_annual_concentrated.xlsx")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
