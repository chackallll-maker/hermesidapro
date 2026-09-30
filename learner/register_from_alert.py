#!/usr/bin/env python3
"""
Registro de señales desde alertas existentes — Learner System

Toma alertas preexistentes (como las del alert_report.md) y las
convierte en señales registradas en el historial de aprendizaje.

Uso:
    python register_from_alert.py alert_report.md    # Registrar señales desde este alerta
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
import uuid

from signal_utils import deduplicate_signals, get_duplicate_info, is_duplicate

BASE_DIR = Path(__file__).parent.parent
LEARNER_DIR = BASE_DIR / "learner"


def parse_alert_file(filepath: Path) -> list[dict]:
    """
    Parsea un archivo de alerta y extrae las señales contenidas.
    Devuelve una lista de señales detectadas.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    signals = []

    # Buscar semáforo para identificar qué cripto tiene alerta
    # Patrón: 🔷 XRP  $1.31  (-10.9% 24h)  → 🔴 ATENCIÓN — rompe soporte $1.39
    semaphore_pattern = re.compile(
        r'(🔷|🟦|⬢)\s+(\w+)\s+\$?([\d.]+)\s+\(([+-]?[\d.]+)%\s+24h\)\s+→\s+(🔴|🟡|🟢)\s+(\w+(?:\s+\w+)*)(?:—\s+(.+))?'
    )

    matches = semaphore_pattern.findall(content)
    for match in matches:
        emoji, crypto, price, change, semaforo, label, detail = match
        change_pct = float(change)
        price_val = float(price)

        # Determinar si hay señal (solo si el semáforo no es NEUTRAL)
        if "NEUTRAL" in semaforo or "sin alerta" in label.lower():
            continue

        # Detectar tipo de señal
        signal_type = None
        direction = None
        prediction = None
        rationale = None
        horizon = 12  # default

        if "rompe soporte" in detail.lower() or "soporte" in detail.lower():
            signal_type = "support_breakdown"
            direction = "BAJISTA"
            prediction = f"Continuación bajista, objetivo siguiente nivel de soporte"
            rationale = f"Ruptura de soporte con movimiento de {abs(change_pct)}% en 24h"
            horizon = 24
        elif "caída fuerte" in detail.lower() or change_pct < -10:
            signal_type = "trend_reversal_pattern" if change_pct < -10 else "support_breakdown"
            direction = "BAJISTA"
            prediction = f"Continuidad de la caída, posible objetivos inferiores"
            rationale = f"Caída de {abs(change_pct)}% en 24h, semáforo 🔴"
            horizon = 12
        elif "suba explosiva" in detail.lower() or change_pct > 10:
            signal_type = "resistance_breakout"
            direction = "ALCISTA"
            prediction = "Continuidad alcista, posible extensión del movimiento"
            rationale = f"Suba de {change_pct}% en 24h, semáforo 🟢"
            horizon = 12
        elif "consolidando" in label.lower():
            # No es señal direccional clara
            continue

        if signal_type is None:
            continue

        # Obtener timestamp del archivo (si está en el título)
        timestamp_match = re.search(r'alerta.*?(\d{2}:\d{2})\s+ARG', content, re.IGNORECASE)
        hora_str = timestamp_match.group(1) if timestamp_match else "12:00"

        # Para el demo, usar fecha de ayer (asumimos que el alerta es reciente)
        # En producción, usar la fecha real del archivo o del sistema
        alert_date = datetime.now(timezone.utc).date() - timedelta(days=1)
        alert_time = datetime.strptime(f"{alert_date.strftime('%Y-%m-%d')} {hora_str}:00", "%Y-%m-%d %H:%M:%S")
        alert_time = alert_time.replace(tzinfo=timezone.utc)

        signal = {
            "id": str(uuid.uuid4()),
            "crypto": crypto,
            "timestamp": alert_time.isoformat(),
            "signal_type": signal_type,
            "direction": direction,
            "prediction": prediction,
            "price_at_signal": price_val,
            "confidence": "MEDIO",  # se puede calibrar con el perfil del especialista
            "rationale": rationale,
            "market_regime": detect_market_regime(content, crypto),
            "horizon_hours": horizon,
            "resolve_by": (alert_time + timedelta(hours=horizon)).isoformat(),
            "resolved": False,
            "outcome": "pendiente"
        }
        signals.append(signal)

    return signals


def detect_market_regime(content: str, crypto: str) -> str:
    """Detecta el régimen de mercado basado en el contenido del alerta."""
    content_lower = content.lower()

    if "noticias" in content_lower or "claridad" in content_lower or "sec" in content_lower or " Ripple" in content:
        if crypto == "XRP":
            return "noticias_Ripple"
    if "volatilidad" in content_lower or "brusco" in content_lower:
        return "alta_volatilidad"
    if "sin noticias" in content_lower or "movimiento técnico" in content_lower:
        return "lateral"
    if "tendencia" in content_lower and "alcista" in content_lower:
        return "tendencia_alcista"
    if "tendencia" in content_lower and "bajista" in content_lower:
        return "tendencia_bajista"

    return "lateral"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Registrar señales desde archivos de alerta")
    parser.add_argument("file", type=str, help="Ruta al archivo de alerta markdown")
    parser.add_argument("--crypto", type=str, help="Filtrar por cripto específica")
    args = parser.parse_args()

    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ Archivo no encontrado: {filepath}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  REGISTRANDO SEÑALES DESDE: {filepath.name}")
    print(f"{'='*60}\n")

    signals = parse_alert_file(filepath)

    if not signals:
        print("   ℹ️  No se detectaron señales direccionales en el archivo.")
        print("   (El alerta podría no contener predicciones, solo datos.)")
        return

    print(f"\n   📋 Señales detectadas: {len(signals)}\n")

    # Cargar señales existentes para detección de duplicados
    existing_by_crypto = {}
    for crypto in ["XRP", "XLM", "HBAR"]:
        json_path = LEARNER_DIR / f"signals-{crypto.lower()}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                existing_by_crypto[crypto] = json.load(f)
        else:
            existing_by_crypto[crypto] = []

    # Detectar duplicados
    print("   🔍 Detectando duplicados...\n")

    filtered_signals = []
    for sig in signals:
        crypto = sig["crypto"]
        existing = existing_by_crypto.get(crypto, [])
        dup = is_duplicate(sig, existing)  # import from signal_utils
        
        if dup is not None:
            dup_info = get_duplicate_info(dup)
            print(f"   ⚠️  DUPLICADO detectado:")
            print(f"      Nueva: {sig['id'][:8]}... {sig['signal_type']} ({sig['direction']}) ${sig['price_at_signal']}")
            print(f"      Existente: {dup_info['existing_id'][:8]}... {dup_info['existing_type']} ({dup_info['existing_direction']}) ${dup_info['existing_price']}")
            print(f"      → No se registrará (duplicado de señal existente)\n")
        else:
            filtered_signals.append(sig)
            print(f"   ✅ {sig['crypto']} — {sig['signal_type']} — NO es duplicado\n")

    if not filtered_signals:
        print("   ℹ️  No hay señales nuevas para registrar (todas eran duplicados).")
        return

    print(f"\n   📋 Señales a registrar: {len(filtered_signals)}\n")

    # Guardar señales en los archivos correspondientes
    for sig in filtered_signals:
        if args.crypto and sig["crypto"] != args.crypto:
            continue

        json_path = LEARNER_DIR / f"signals-{sig['crypto'].lower()}.json"

        # Cargar existentes o crear vacío
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        else:
            existing = []

        # Agregar nueva señal
        existing.append(sig)

        # Guardar
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print(f"   💾 Guardada en {json_path.name} (total: {len(existing)} señales)")

    print(f"\n✅ Registro completado.\n")


if __name__ == "__main__":
    main()
