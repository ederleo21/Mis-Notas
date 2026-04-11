import pandas as pd
import os

files = [
    "CALIFICACIONES DEL PRIMER TRIMESTRE  DE 3ero Mónica 2025(Recuperado automáticamente).xlsx",
    "CUADRO DE CALIFICACION DE Eder 3ERO B.xlsx",
    "REPORTE_CALIF_BASICA_ELEMENTAL Eder _2025.xlsx"
]

for file in files:
    print(f"--- Analyzing {file} ---")
    if os.path.exists(file):
        try:
            # Read only the first few rows and columns to get an idea
            df = pd.read_excel(file, header=None).iloc[:20, :15]
            print(df.to_string())
            print("\n")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    else:
        print(f"File {file} not found.")
