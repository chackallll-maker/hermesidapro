#!/usr/bin/env python3
"""
Utilidades para detección de señales duplicadas en el sistema de aprendizaje.

Un duplicado es una señal con el mismo:
- signal_type
- crypto
- direction
- price_at_signal (dentro de una tolerancia del 0.5%)
- rationale_hash (hash del texto de rationale)

Esto evita que el orquestador registre múltiples señales idénticas
porque "ya existen 3 señales pendientes con el mismo razonamiento"
sin tener una lógica automática que lo haga.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def compute_signal_hash(signal: dict, price_tolerance_pct: float = 0.5) -> str:
    """
    Calcula un hash identificador para una señal.

    El hash combina:
    - signal_type
    - crypto
    - direction
    - price_at_signal (redondeado a la tolerancia especificada)
    - rationale (hash del texto, normalizado)

    Args:
        signal: dict con los campos de la señal
        price_tolerance_pct: tolerancia para considerar precios iguales (default 0.5%)

    Returns:
        String hash hex de 32 caracteres
    """
    signal_type = signal.get("signal_type", "")
    crypto = signal.get("crypto", "")
    direction = signal.get("direction", "")
    price = signal.get("price_at_signal")
    rationale = signal.get("rationale", "")

    # Normalizar precio: redondear a tolerancia para igualdad aproximada
    if price is not None:
        price_rounded = round(price / (price_tolerance_pct / 100)) * (price_tolerance_pct / 100)
        price_str = f"{price_rounded:.6f}"
    else:
        price_str = "None"

    # Normalizar rationale: lowercase, quitar espacios extra
    rationale_normalized = " ".join(rationale.lower().split()) if rationale else ""

    # Crear string canonical para hashing
    canonical = f"{signal_type}|{crypto}|{direction}|{price_str}|{rationale_normalized}"

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def is_duplicate(new_signal: dict, existing_signals: list[dict],
                 price_tolerance_pct: float = 0.5,
                 same_type_only: bool = True) -> dict | None:
    """
    Detecta si una nueva señal es duplicado de una existente.

    Args:
        new_signal: la señal que se quiere registrar
        existing_signals: lista de señales ya registradas
        price_tolerance_pct: tolerancia de precio para considerar iguales
        same_type_only: si True, solo compara con señales del mismo tipo

    Returns:
        El signal existente que es duplicado, o None si no hay duplicado
    """
    new_hash = compute_signal_hash(new_signal, price_tolerance_pct)
    new_type = new_signal.get("signal_type", "")
    new_crypto = new_signal.get("crypto", "")
    new_price = new_signal.get("price_at_signal")

    for existing in existing_signals:
        # Filtrar por cripto (siempre)
        if existing.get("crypto", "").upper() != new_crypto.upper():
            continue

        # Filtrar por tipo si se solicita
        if same_type_only and existing.get("signal_type", "") != new_type:
            continue

        # Calcular hash del existente
        existing_hash = compute_signal_hash(existing, price_tolerance_pct)

        if existing_hash == new_hash:
            # Hash coincide → es duplicado
            return existing

        # Verificación alternativa: mismo tipo, mismo precio aproximado,
        # misma dirección, y rationale muy similar (sin hash exacto)
        if same_type_only and existing.get("signal_type") == new_type:
            existing_price = existing.get("price_at_signal")
            existing_dir = existing.get("direction", "")
            new_dir = new_signal.get("direction", "")

            if (existing_price is not None and new_price is not None and
                    existing_dir == new_dir and
                    abs(existing_price - new_price) / new_price * 100 <= price_tolerance_pct):
                # Precios similares y misma dirección → posible duplicado
                # Verificar similitud del rationale
                existing_rationale = existing.get("rationale", "").lower()
                new_rationale = new_signal.get("rationale", "").lower()

                # Si el rationale es muy corto o vacío, no podemos determinar
                if not existing_rationale or not new_rationale:
                    continue

                # Calcular similitud básica: palabras en común
                existing_words = set(existing_rationale.split())
                new_words = set(new_rationale.split())
                common = existing_words & new_words

                # Si el 50% o más de las palabras del rational más corto están en el otro
                shorter = min(len(existing_words), len(new_words))
                longer = max(len(existing_words), len(new_words))

                if shorter >= 5 and (len(common) / shorter) >= 0.5:
                    return existing

    return None


def get_duplicate_info(duplicate: dict | None) -> dict:
    """
    Formatea información sobre un duplicado detectado para logging/informe.

    Args:
        duplicate: el signal existente que es duplicado, o None

    Returns:
        dict con información formateada del duplicado
    """
    if duplicate is None:
        return {"is_duplicate": False}

    return {
        "is_duplicate": True,
        "existing_id": duplicate.get("id", "?"),
        "existing_type": duplicate.get("signal_type", ""),
        "existing_direction": duplicate.get("direction", ""),
        "existing_price": duplicate.get("price_at_signal"),
        "existing_timestamp": duplicate.get("timestamp", ""),
        "existing_resolved": duplicate.get("resolved", False),
        "existing_outcome": duplicate.get("outcome", ""),
        "existing_hash": compute_signal_hash(duplicate),
    }


def deduplicate_signals(new_signals: list[dict],
                        existing_signals: list[dict],
                        price_tolerance_pct: float = 0.5) -> tuple[list[dict], list[dict]]:
    """
    Filtra una lista de señales nuevas, eliminando las que son duplicados
    de señales ya existentes.

    Args:
        new_signals: señales que se quieren registrar
        existing_signals: señales ya registradas
        price_tolerance_pct: tolerancia de precio para igualdad

    Returns:
        (señales_a_registrar, señales_duplicadas)
        - señales_a_registrar: nuevas señales que no son duplicados
        - señales_duplicadas: info de cada duplicado detectado
    """
    to_register = []
    duplicates = []

    for new_sig in new_signals:
        dup = is_duplicate(new_sig, existing_signals, price_tolerance_pct)
        if dup is not None:
            duplicates.append({
                "new_signal": new_sig,
                "duplicate_info": get_duplicate_info(dup),
            })
        else:
            to_register.append(new_sig)

    return to_register, duplicates


if __name__ == "__main__":
    # Demo de funcionamiento
    print("=" * 60)
    print("  DEMO: Detección de señales duplicadas")
    print("=" * 60)

    existing = [
        {
            "id": "abc123",
            "crypto": "HBAR",
            "signal_type": "rsi_overbought_reversal",
            "direction": "BAJISTA",
            "price_at_signal": 0.12000,
            "rationale": "RSI 1h en 86 = sobrecompra extrema. Precio en maximo diario $0.11418. Fear & Greed 74 (Greed).",
            "timestamp": "2026-09-28T06:09:05Z",
            "resolved": False,
            "outcome": "pendiente",
        },
        {
            "id": "def456",
            "crypto": "XRP",
            "signal_type": "resistance_breakout",
            "direction": "ALCISTA",
            "price_at_signal": 1.41,
            "rationale": "XRP rompe resistencia $1.41 con movimiento +8.52% 24h",
            "timestamp": "2026-09-19T15:15:00Z",
            "resolved": True,
            "outcome": "error",
        },
    ]

    # Señal duplicada exacta (misma crypto, tipo, dirección, precio, rationale)
    nueva_duplicada = {
        "id": "nueva-789",
        "crypto": "HBAR",
        "signal_type": "rsi_overbought_reversal",
        "direction": "BAJISTA",
        "price_at_signal": 0.12010,  # 0.08% diferencia → dentro de tolerancia 0.5%
        "rationale": "RSI 1h en 86 = sobrecompra extrema. Precio en maximo diario $0.11418. Fear & Greed 74 (Greed).",
        "timestamp": "2026-09-28T06:32:00Z",
        "resolved": False,
        "outcome": "pendiente",
    }

    # Señal nueva (diferente crypto)
    nueva_unica = {
        "id": "nueva-012",
        "crypto": "XLM",
        "signal_type": "rsi_overbought_reversal",
        "direction": "BAJISTA",
        "price_at_signal": 0.21000,
        "rationale": "XLM RSI 1h en 70 = sobrecompra, posible corrección",
        "timestamp": "2026-09-28T12:00:00Z",
        "resolved": False,
        "outcome": "pendiente",
    }

    print("\n--- Prueba 1: Duplicado por hash exacto ---")
    dup = is_duplicate(nueva_duplicada, existing)
    info = get_duplicate_info(dup)
    print(f"  ¿Es duplicado? {info['is_duplicate']}")
    if info["is_duplicate"]:
        print(f"  ID existente: {info['existing_id']}")
        print(f"  Tipo: {info['existing_type']}")
        print(f"  Hash: {info['existing_hash'][:16]}...")

    print("\n--- Prueba 2: Señal única (diferente crypto) ---")
    dup2 = is_duplicate(nueva_unica, existing)
    info2 = get_duplicate_info(dup2)
    print(f"  ¿Es duplicado? {info2['is_duplicate']}")

    print("\n--- Prueba 3: Deduplicación por lotes ---")
    nuevas = [nueva_duplicada, nueva_unica]
    a_registrar, duplicados = deduplicate_signals(nuevas, existing)
    print(f"  Total nuevo: {len(nuevas)}")
    print(f"  A registrar: {len(a_registrar)}")
    print(f"  Duplicados: {len(duplicados)}")
    for d in duplicados:
        print(f"    → {d['new_signal']['id'][:8]}... duplicado de {d['duplicate_info']['existing_id'][:8]}...")

    print("\n✅ Demo completada")
