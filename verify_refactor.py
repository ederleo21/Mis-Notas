import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academic_sys.settings')
try:
    django.setup()
    from grades.views import dashboard, academic, students, grading, reports
    print("SUCCESS: All view modules imported correctly.")
except Exception as e:
    print(f"FAILURE: {e}")
    sys.exit(1)
