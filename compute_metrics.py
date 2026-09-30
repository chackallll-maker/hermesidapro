import json
import sys

def main():
    try:
        with open('learner/orchestrator_signals.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: orchestrator_signals.json is not a list")
        sys.exit(1)

    total_runs = len(data)
    alertas_generadas = 0
    near_misses = 0

    for run in data:
        # Check if this run has any alerta: true in any crypto
        criptos = run.get('criptos', {})
        for crypto_info in criptos.values():
            if isinstance(crypto_info, dict) and crypto_info.get('alerta') == True:
                alertas_generadas += 1
                break  # count only once per run
        # Count near_misses: any crypto with near_miss: true?
        for crypto_info in criptos.values():
            if isinstance(crypto_info, dict) and crypto_info.get('near_miss') == True:
                near_misses += 1
                break  # count only once per run

    if total_runs >= 5:
        perc_alertas = (alertas_generadas / total_runs) * 100 if total_runs > 0 else 0
        perc_near_misses = (near_misses / total_runs) * 100 if total_runs > 0 else 0
        summary = f"Orquestador: {total_runs} runs, {alertas_generadas} alertas ({perc_alertas:.1f}%), {near_misses} near-misses ({perc_near_misses:.1f}%)"
    else:
        summary = f"Orquestador: datos insuficientes aún ({total_runs} runs)"

    print(summary)

if __name__ == '__main__':
    main()
