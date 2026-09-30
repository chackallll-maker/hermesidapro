#!/usr/bin/env python
"""
Resuelve señales pendientes del sistema de aprendizaje cripto.

Para cada señal con `resolved=false` y `resolve_by < ahora()`:
1. Obtener precio actual de la cripto vía CoinGecko
2. Comparar con price_at_signal
3. Determinar outcome según el tipo de señal y horizon
4. Actualizar el JSON con outcome, outcome_detail, resolved=true

Uso: python resolve_signals.py
Requiere: requests, json, uuid (stdlib)
"""

import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Config
PROJECT_DIR = Path("C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor")
BINANCE_SYMBOLS = {
    "XRP": "XRPUSDT",
    "XLM": "XLMUSDT",
    "HBAR": "HBARUSDT",
}

CRYPTO_MAP = {
    "XRP": "ripple",
    "XLM": "stellar",
    "HBAR": "hedera-hashgraph",
}

# Criterio de acierto por tipo de señal
# (precio final vs precio de señal, en %)
ACCION_CRITERIA = {
    "rsi_overbought_reversal": ("baja", 2.0),       # precio baja >=2%
    "rsi_oversold_rebound": ("sube", 2.0),           # precio sube >=2%
    "oversold_bounce_ma7": ("sube", 1.5),            # rebote desde sobreventa: precio sube >=1.5%
    "macd_bullish_cross": ("mayor", 0.0),            # precio mayor al de señal
    "macd_bearish_cross": ("menor", 0.0),            # precio menor al de señal
    "support_breakdown": ("por_debajo", 0.0),        # precio por debajo del soporte
    "resistance_breakout": ("por_encima", 0.0),     # precio por encima de la resistencia
    "news_positive_impact": ("sube", 1.5),           # precio sube >=1.5%
    "news_negative_impact": ("baja", 1.5),           # precio baja >=1.5%
    "sentiment_shift": ("coincide", 0.0),            # dirección coincide con sentimiento
    "fear_greed_extreme": ("reversion", 3.0),        # reversión >=3% en dirección opuesta
    "whale_accumulation": ("no_baja", 0.0),          # precio no baja significativamente
    "trend_continuation": ("continua", 0.0),
    "trend_reversal_pattern": ("revierte", 0.0),
    "volume_confirmation": ("confirma", 0.0),
    "volume_divergence": ("diverge", 0.0),
    "event_catalyst": ("impacto", 0.0),
    "regime_change": ("cambio", 0.0),
    "support_retest": ("sube", 1.5),              # tras retest del soporte, continua al alza
    "support_hold_continuation": ("sube", 1.5),   # sostiene el soporte y continua
    "consolidation_range": ("banda", 2.5),        # se mantiene dentro del rango +/-2.5%
    "resistance_rejection": ("baja", 1.5),        # rechazo en resistencia -> precio baja
    "breakout_confirmation": ("por_encima", 0.0), # confirmacion de ruptura >= referencia
    "momentum_decay": ("baja", 1.0),              # perdida de momentum -> >=1% a la baja
}


def get_current_price(crypto_id: str, retries: int = 4) -> float:
    """Obtener precio actual desde CoinGecko simple API, con reintentos y backoff.

    CoinGecko_free sin key tiene rate limit estricto (~10-30 req/min). Un unico
    429 dejaba la senal sin resolver para siempre, asi que se reintenta.
    """
    import time
    import requests

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_id}&vs_currencies=usd"
    headers = {"accept": "application/json", "user-agent": "hermes-crypto-monitor/1.0"}

    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=20, headers=headers)
            if resp.status_code == 429:
                wait = 8 * (attempt + 1)
                print(f"  ⏳ Rate limit (429), reintento {attempt+1}/{retries} en {wait}s",
                      file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return data[crypto_id]["usd"]
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(4 * (attempt + 1))
    if last_err:
        print(f"  ERROR obteniendo precio para {crypto_id}: {last_err}", file=sys.stderr)
    return None


def get_price_fallback(symbol: str) -> float:
    """Precio via Binance public ticker.

    CoinGecko free esta duro rate-limited (429) y deja senales sin resolver.
    Binance no exige key para el ticker publico, asi que se usa como fallback.
    """
    import requests
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        return float(resp.json()["price"])
    except Exception as e:
        print(f"  ERROR precio fallback Binance {symbol}: {e}", file=sys.stderr)
        return None


def compute_outcome(signal: dict, current_price: float) -> tuple:
    """
    Determina outcome para una señal dada el precio actual.
    Retorna (outcome, outcome_detail, accuracy_note)
    """
    signal_type = signal.get("signal_type", "unknown")
    direction = signal.get("direction", "NEUTRO")
    price_at_signal = signal.get("price_at_signal")
    prediction = signal.get("prediction", "")
    criteria = ACCION_CRITERIA.get(signal_type)

    signal_id = signal.get("id", "?")
    debug_log = {
        "signal_id": signal_id,
        "crypto": signal.get("crypto", "?"),
        "signal_type": signal_type,
        "direction": direction,
        "price_at_signal": price_at_signal,
        "current_price": None,
        "pct_change": None,
        "criteria": None,
        "comparison": None,
        "threshold": None,
        "steps": [],
        "outcome": None,
        "accuracy_note": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if criteria is None:
        # Bug silencioso historico: estos 3 finish como 'neutral' y contaminan
        # la estadistica. Ahora queda explicito para que se detecte al instante.
        print(f"  ⚠️  TIPO DE SEÑAL SIN CRITERIO: '{signal_type}' — "
              f"agregarlo a ACCION_CRITERIA en resolve_signals.py", file=sys.stderr)
        debug_log["criteria"] = "NO DEFINIDO"
        debug_log["steps"].append("criterio_no_definido → neutral")
        debug_log["outcome"] = "neutral"
        debug_log["accuracy_note"] = "Sin criterio definido"
        _write_debug_log(debug_log)
        return ("neutral", f"Tipo de señal desconocido ({signal_type})", "Sin criterio definido")

    if price_at_signal is None or current_price is None:
        if price_at_signal is None:
            debug_log["steps"].append("sin_precio_señal → neutral")
        else:
            debug_log["steps"].append("sin_precio_actual → neutral")
        debug_log["outcome"] = "neutral"
        debug_log["accuracy_note"] = "Datos incompletos"
        _write_debug_log(debug_log)
        return ("neutral", "Precio no disponible para comparación", "Datos incompletos")

    pct_change = ((current_price - price_at_signal) / price_at_signal) * 100
    threshold = criteria[1]
    comparison = criteria[0]

    debug_log["current_price"] = current_price
    debug_log["pct_change"] = round(pct_change, 4)
    debug_log["criteria"] = criteria[0]
    debug_log["comparison"] = comparison
    debug_log["threshold"] = threshold
    debug_log["steps"].append(f"pct_change={pct_change:+.4f}% | comparison={comparison} | threshold={threshold}")

    # Una señal NEUTRO no hace claim direccional: no se puede acertar ni fallar.
    # Se evalúa solo el rango (banda) o queda neutral.
    if direction == "NEUTRO" and comparison != "banda":
        return (
            "neutral",
            f"Precio: ${current_price:.4f} vs señal ${price_at_signal:.4f} ({pct_change:+.2f}%) — "
            f"señal NEUTRO, sin claim direccional que evaluar",
            "señal neutral — no se evaluó dirección",
        )

    # Banda muerta: movimientos menores a DEAD_BAND_PCT no cuentan como acierto
    # ni como error, solo como neutral (el mercado essentially no se movió).
    DEAD_BAND_PCT = 0.5

    outcome = "neutral"
    detail = f"Precio: ${current_price:.4f} vs señal ${price_at_signal:.4f} ({pct_change:+.2f}%)"

    if comparison == "baja":
        if abs(pct_change) < DEAD_BAND_PCT:
            outcome = "neutral"
        elif direction == "BAJISTA" and pct_change <= -threshold:
            outcome = "acierto"
        elif direction == "ALCISTA" and pct_change >= threshold:
            outcome = "error"
        else:
            outcome = "error" if abs(pct_change) < threshold else ("acierto" if pct_change < 0 else "error")

    elif comparison == "sube":
        if abs(pct_change) < DEAD_BAND_PCT:
            outcome = "neutral"
        elif direction == "ALCISTA" and pct_change >= threshold:
            outcome = "acierto"
        elif direction == "BAJISTA" and pct_change <= -threshold:
            outcome = "error"
        else:
            outcome = "error" if abs(pct_change) < threshold else ("acierto" if pct_change > 0 else "error")

    elif comparison == "mayor":
        if current_price > price_at_signal:
            outcome = "acierto" if direction == "ALCISTA" else "error"
        else:
            outcome = "error" if direction == "ALCISTA" else "acierto"

    elif comparison == "menor":
        if current_price < price_at_signal:
            outcome = "acierto" if direction == "BAJISTA" else "error"
        else:
            outcome = "error" if direction == "BAJISTA" else "acierto"

    elif comparison == "no_baja":
        if pct_change >= -1.0:
            outcome = "acierto" if direction == "ALCISTA" else "neutral"
        else:
            outcome = "error"

    elif comparison == "coincide":
        # Sentimiento shift: dirección del precio coincide con la dirección del cambio
        if (pct_change > 0 and direction == "ALCISTA") or (pct_change < 0 and direction == "BAJISTA"):
            outcome = "acierto"
        else:
            outcome = "error"

    elif comparison == "banda":
        # consolidation_range: la señal predice rango. Acierto si el precio
        # se mantuvo dentro de +/- threshold al resolver.
        if abs(pct_change) <= threshold:
            outcome = "acierto" if direction in ("NEUTRO", "ALCISTA", "BAJISTA") else "neutral"
        elif abs(pct_change) <= threshold * 2:
            outcome = "neutral"
        else:
            outcome = "error"

    elif comparison == "reversion":
        # Fear & greed extreme: reversión >=3% en dirección opuesta
        if abs(pct_change) >= threshold:
            if (pct_change < 0 and direction == "ALCISTA") or (pct_change > 0 and direction == "BAJISTA"):
                outcome = "acierto"
            else:
                outcome = "error"
        else:
            outcome = "neutral"

    else:
        # Para criterios no manejados, usar porcentaje
        if abs(pct_change) >= threshold:
            if (pct_change > 0 and direction == "ALCISTA") or (pct_change < 0 and direction == "BAJISTA"):
                outcome = "acierto"
            else:
                outcome = "error"
        else:
            outcome = "neutral"

    # Loguear pasos intermedios según la rama que se ejecutó
    if comparison == "baja":
        if abs(pct_change) < DEAD_BAND_PCT:
            debug_log["steps"].append(f"baja: |Δ|={abs(pct_change):.2f}% < {DEAD_BAND_PCT}% → neutral (dead band)")
        elif direction == "BAJISTA" and pct_change <= -threshold:
            debug_log["steps"].append(f"baja: BAJISTA + Δ={pct_change:+.2f}% ≤ -{threshold}% → ACIERTO")
        elif direction == "ALCISTA" and pct_change >= threshold:
            debug_log["steps"].append(f"baja: ALCISTA + Δ={pct_change:+.2f}% ≥ +{threshold}% → ERROR (se esperaba baja)")
        else:
            debug_log["steps"].append(f"baja: condición mixta Δ={pct_change:+.2f}% → ERROR")
    elif comparison == "sube":
        if abs(pct_change) < DEAD_BAND_PCT:
            debug_log["steps"].append(f"sube: |Δ|={abs(pct_change):.2f}% < {DEAD_BAND_PCT}% → neutral (dead band)")
        elif direction == "ALCISTA" and pct_change >= threshold:
            debug_log["steps"].append(f"sube: ALCISTA + Δ={pct_change:+.2f}% ≥ +{threshold}% → ACIERTO")
        elif direction == "BAJISTA" and pct_change <= -threshold:
            debug_log["steps"].append(f"sube: BAJISTA + Δ={pct_change:+.2f}% ≤ -{threshold}% → ERROR (se esperaba suba)")
        else:
            debug_log["steps"].append(f"sube: condición mixta Δ={pct_change:+.2f}% → ERROR")
    elif comparison == "mayor":
        if current_price > price_at_signal:
            debug_log["steps"].append(f"mayor: precio ${current_price} > señal ${price_at_signal} → {'ACIERTO' if direction=='ALCISTA' else 'ERROR'}")
        else:
            debug_log["steps"].append(f"mayor: precio ${current_price} ≤ señal ${price_at_signal} → {'ERROR' if direction=='ALCISTA' else 'ACIERTO'}")
    elif comparison == "menor":
        if current_price < price_at_signal:
            debug_log["steps"].append(f"menor: precio ${current_price} < señal ${price_at_signal} → {'ACIERTO' if direction=='BAJISTA' else 'ERROR'}")
        else:
            debug_log["steps"].append(f"menor: precio ${current_price} ≥ señal ${price_at_signal} → {'ERROR' if direction=='BAJISTA' else 'ACIERTO'}")
    elif comparison == "no_baja":
        if pct_change >= -1.0:
            debug_log["steps"].append(f"no_baja: Δ={pct_change:+.2f}% ≥ -1.0% → ACIERTO (no bajó significativamente)")
        else:
            debug_log["steps"].append(f"no_baja: Δ={pct_change:+.2f}% < -1.0% → ERROR")
    elif comparison == "coincide":
        if (pct_change > 0 and direction == "ALCISTA") or (pct_change < 0 and direction == "BAJISTA"):
            debug_log["steps"].append(f"coincide: dirección coincide (Δ={pct_change:+.2f}%, dir={direction}) → ACIERTO")
        else:
            debug_log["steps"].append(f"coincide: dirección NO coincide (Δ={pct_change:+.2f}%, dir={direction}) → ERROR")
    elif comparison == "banda":
        if abs(pct_change) <= threshold:
            debug_log["steps"].append(f"banda: |Δ|={abs(pct_change):.2f}% ≤ {threshold}% → ACIERTO (dentro del rango)")
        elif abs(pct_change) <= threshold * 2:
            debug_log["steps"].append(f"banda: |Δ|={abs(pct_change):.2f}% ≤ {threshold*2:.1f}% → neutral (rango ampliado)")
        else:
            debug_log["steps"].append(f"banda: |Δ|={abs(pct_change):.2f}% > {threshold*2:.1f}% → ERROR (salio del rango)")
    elif comparison == "reversion":
        if abs(pct_change) >= threshold:
            if (pct_change < 0 and direction == "ALCISTA") or (pct_change > 0 and direction == "BAJISTA"):
                debug_log["steps"].append(f"reversion: |Δ|={abs(pct_change):.2f}% ≥ {threshold}% + dirección opuesta → ACIERTO (reversión)")
            else:
                debug_log["steps"].append(f"reversion: |Δ|={abs(pct_change):.2f}% ≥ {threshold}% pero dirección igual → ERROR")
        else:
            debug_log["steps"].append(f"reversion: |Δ|={abs(pct_change):.2f}% < {threshold}% → neutral (sin reversión suficiente)")
    else:
        if abs(pct_change) >= threshold:
            if (pct_change > 0 and direction == "ALCISTA") or (pct_change < 0 and direction == "BAJISTA"):
                debug_log["steps"].append(f"default: |Δ|={abs(pct_change):.2f}% ≥ {threshold}% + dirección ok → ACIERTO")
            else:
                debug_log["steps"].append(f"default: |Δ|={abs(pct_change):.2f}% ≥ {threshold}% + dirección no ok → ERROR")
        else:
            debug_log["steps"].append(f"default: |Δ|={abs(pct_change):.2f}% < {threshold}% → neutral")

    accuracy_note = ""
    if outcome == "acierto" and comparison == "banda":
        accuracy_note = f"dentro del rango previsto (+/-{threshold}%)"
    elif outcome == "acierto" and abs(pct_change) < threshold * 0.5:
        accuracy_note = "acierto pero por margen pequeño"
    elif outcome == "error" and abs(pct_change) < threshold * 0.5:
        accuracy_note = "error por margen estrecho — casi acertó"
    elif outcome == "neutral" and abs(pct_change) < DEAD_BAND_PCT and comparison != "banda":
        accuracy_note = "movimiento despreciable (<0.5%) — sin veredicto"

    debug_log["accuracy_note"] = accuracy_note
    debug_log["outcome"] = outcome
    debug_log["final"] = f"{outcome.upper()} | Δ={pct_change:+.2f}% | umbral={threshold}% | {comparison}"

    _write_debug_log(debug_log)

    return (outcome, detail, accuracy_note)


def _write_debug_log(entry: dict) -> None:
    """Escribe una entrada de log de debug en debug-<crypto>.jsonl"""
    crypto = entry.get("crypto", "unknown")
    log_path = PROJECT_DIR / "learner" / f"debug-{crypto.lower()}.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")



def resolve_signals():
    """Resuelve todas las señales pendientes."""
    now = datetime.now(timezone.utc)

    for crypto in ["XRP", "XLM", "HBAR"]:
        signals_file = PROJECT_DIR / "learner" / f"signals-{crypto.lower()}.json"
        if not signals_file.exists():
            print(f"⚠️  No hay archivo de señales para {crypto}")
            continue

        with open(signals_file, "r") as f:
            signals = json.load(f)

        crypto_id = CRYPTO_MAP.get(crypto)
        if not crypto_id:
            print(f"⚠️  No hay ID CoinGecko para {crypto}")
            continue

        updated = 0
        for signal in signals:
            if signal.get("resolved") is True:
                continue

            resolve_by_str = signal.get("resolve_by")
            if not resolve_by_str:
                continue

            try:
                resolve_by = datetime.fromisoformat(resolve_by_str.replace("Z", "+00:00"))
            except Exception:
                continue

            if resolve_by > now:
                continue  # Todavía no llegó el horizonte

            print(f"\n📊 Resolviendo señal {crypto} — {signal.get('id','?')} "
                  f"({signal.get('signal_type','?')}) — resolve_by: {resolve_by_str}")

            current_price = get_current_price(crypto_id)
            if current_price is None:
                # CoinGecko caido/rate-limited: probar Binance
                symbol = BINANCE_SYMBOLS.get(crypto)
                if symbol:
                    current_price = get_price_fallback(symbol)
                    if current_price is not None:
                        print(f"  ↪️  Precio via fallback Binance: ${current_price}")
            if current_price is None:
                print("  ⏭️  No se pudo obtener precio de ninguna fuente, saltando")
                continue

            outcome, detail, accuracy_note = compute_outcome(signal, current_price)
            signal["resolved"] = True
            signal["outcome"] = outcome
            signal["outcome_detail"] = detail
            if accuracy_note:
                signal["accuracy_note"] = accuracy_note

            print(f"  → Outcome: {outcome} | {detail}")
            if accuracy_note:
                print(f"  → Nota: {accuracy_note}")

            updated += 1

        if updated > 0:
            with open(signals_file, "w") as f:
                json.dump(signals, f, indent=2)
            print(f"  ✅ {updated} señal(es) actualizada(s) en {signals_file.name}")
        else:
            print(f"  ✅ {crypto}: no hay señales pendientes para resolver")


if __name__ == "__main__":
    print("=" * 60)
    print("🔍 Resolviendo señales pendientes del sistema de aprendizaje")
    print("=" * 60)
    resolve_signals()
    print("\n✅ Terminado.")
