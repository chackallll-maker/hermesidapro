import json
import os

file_path = 'orchestrator_signals.json'
if not os.path.exists(file_path):
    print('Orquestador: archivo no encontrado')
    exit(0)

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f'Orquestador: error al leer datos - {str(e)}')
    exit(0)

if isinstance(data, list):
    total_runs = len(data)
    alertas = sum(1 for x in data if x.get('alerta_generada') == True)
    near_misses = sum(1 for x in data if x.get('near_miss') == True)
    if total_runs > 0:
        p_alertas = round((alertas / total_runs) * 100)
        p_near_misses = round((near_misses / total_runs) * 100)
    else:
        p_alertas = 0
        p_near_misses = 0
    if total_runs >= 5:
        print(f'Orquestador: {total_runs} runs, {alertas} alertas ({p_alertas}%), {near_misses} near-misses ({p_near_misses}%)')
    else:
        print(f'Orquestador: datos insuficientes aún ({total_runs} runs)')
else:
    print('Orquestador: datos insuficientes aún (formato de datos inesperado)')
