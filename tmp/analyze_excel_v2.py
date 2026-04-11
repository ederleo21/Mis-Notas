import pandas as pd
import os

files = [
    "CALIFICACIONES DEL PRIMER TRIMESTRE  DE 3ero Mónica 2025(Recuperado automáticamente).xlsx",
    "CUADRO DE CALIFICACION DE Eder 3ERO B.xlsx",
    "REPORTE_CALIF_BASICA_ELEMENTAL Eder _2025.xlsx"
]

output_file = "analysis_results.txt"

with open(output_file, "w", encoding="utf-8") as f:
    for file in files:
        f.write(f"--- Analyzing {file} ---\n")
        if os.path.exists(file):
            try:
                # Read all sheets to see what's inside
                xl = pd.ExcelFile(file)
                f.write(f"Sheets: {xl.sheet_names}\n")
                for sheet in xl.sheet_names:
                    f.write(f"\nSheet: {sheet}\n")
                    df = pd.read_excel(file, sheet_name=sheet, header=None).iloc[:30, :20]
                    f.write(df.to_string())
                    f.write("\n")
                f.write("\n")
            except Exception as e:
                f.write(f"Error reading {file}: {e}\n")
        else:
            f.write(f"File {file} not found.\n")

print(f"Analysis written to {output_file}")
