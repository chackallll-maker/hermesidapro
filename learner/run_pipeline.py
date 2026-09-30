#!/usr/bin/env python3
"""Runner del pipeline de aprendizaje automático.
Ejecuta en secuencia:
1. resolve_signals.py — resuelve señales pendientes
2. analyze.py --update-profiles — actualiza perfiles de especialistas
3. xp_tracker.py --update — recalcular niveles y XP
"""
import subprocess
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent  # Raíz del proyecto (crypto-monitor/)

def run_script(script_path: str, description: str) -> bool:
    """Ejecuta un script Python y retorna True si salió bien."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}")
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / script_path)],
        cwd=str(PROJECT_DIR),
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}", file=sys.stderr)
    success = result.returncode == 0
    status = "✅ OK" if success else f"❌ ERROR (código {result.returncode})"
    print(f"\n{status}")
    return success

def main():
    print("=" * 60)
    print("  PIPELINE DE APRENDIZAJE AUTOMÁTICO")
    print(f"  {PROJECT_DIR}")
    print("=" * 60)
    
    results = {}
    
    # Paso 1: Resolver señales pendientes
    results["resolve"] = run_script("resolve_signals.py", "1. Resolviendo señales pendientes")
    
    # Paso 2: Actualizar perfiles de especialistas
    results["analyze"] = run_script("learner/analyze.py", "2. Actualizando perfiles de especialistas")
    
    # Paso 3: Recalcular niveles y XP
    results["xp"] = run_script("learner/xp_tracker.py", "3. Recalculando niveles y XP")
    
    # Resumen final
    print("\n" + "=" * 60)
    print("  RESUMEN DEL PIPELINE")
    print("=" * 60)
    for step, ok in results.items():
        print(f"  {'✅' if ok else '❌'} {step}")
    
    all_ok = all(results.values())
    print(f"\n{'✅ Pipeline completado Exitosamente' if all_ok else '❌ El pipeline tuvo errores'}")
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
