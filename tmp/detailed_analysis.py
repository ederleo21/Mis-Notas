import pandas as pd
import json

files = [
    "CALIFICACIONES DEL PRIMER TRIMESTRE  DE 3ero Mónica 2025(Recuperado automáticamente).xlsx",
    "CUADRO DE CALIFICACION DE Eder 3ERO B.xlsx",
    "REPORTE_CALIF_BASICA_ELEMENTAL Eder _2025.xlsx"
]

results = {}

for file in files:
    try:
        xl = pd.ExcelFile(file)
        results[file] = {"sheets": xl.sheet_names, "content": {}}
        for sheet in xl.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet)
            results[file]["content"][sheet] = {
                "columns": [str(c) for c in df.columns.tolist()],
                "sample_rows": df.head(5).astype(str).values.tolist()
            }
    except Exception as e:
        results[file] = {"error": str(e)}

with open("excel_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("Analysis complete. Check excel_analysis.json")
