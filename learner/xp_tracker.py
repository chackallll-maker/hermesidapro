#!/usr/bin/env python3
"""
Tracker de Niveles y XP del Bot — Sistema de Aprendizaje Gamificado

Calcula el nivel, XP y barra de progreso del bot para cada cripto
y para el nivel global, basándose en las señales resueltas en
signals-<crypto>.json.

No modifica los archivos de señales ni los perfiles directamente —
solo lee y calcula. Para actualizar el estado, usar update_progress().

Uso:
    python xp_tracker.py                     # Mostrar progreso actual
    python xp_tracker.py --crypto XRP         # Solo XRP
    python xp_tracker.py --update             # Actualizar progress.json
    python xp_tracker.py --crypto XRP --update  # Actualizar solo XRP
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# Directorio base del proyecto
BASE_DIR = Path(__file__).parent.parent
LEARNER_DIR = BASE_DIR / "learner"

# Niveles del sistema
NIVELES = [
    {"nivel": 1, "nombre": "Bot Novato", "xp_min": 0, "xp_next": 50, "capacidades": "Análisis básico (RSI, MACD, precios). Recomendación: HOLD/espere."},
    {"nivel": 2, "nombre": "Bot Aprendiz", "xp_min": 50, "xp_next": 200, "capacidades": "Volumen para confirmar señales. Soportes/resistencias. Recomendación: compra/venda si indicadores respaldan."},
    {"nivel": 3, "nombre": "Bot Experimentado", "xp_min": 200, "xp_next": 500, "capacidades": "Análisis fundamental básico. Sentimiento (Fear&Greed, noticias). Calibración de confianza por régimen."},
    {"nivel": 4, "nombre": "Bot Analista", "xp_min": 500, "xp_next": 1000, "capacidades": "Backtest integrado. Puede emitir ALTO confianza cuando respaldado. Especifica niveles de entrada/target/stop-loss."},
    {"nivel": 5, "nombre": "Bot Especialista", "xp_min": 1000, "xp_next": 2000, "capacidades": "Conoce patrones crytoespecíficos. Correlación con BTC. Detecta régimen de mercado y ajusta criterio."},
    {"nivel": 6, "nombre": "Bot Maestro", "xp_min": 2000, "xp_next": 3000, "capacidades": "Umbrales ajustados — solo señales de alta calidad. ALTO confianza con múltiples confirmaciones. Puede decir 'no hay señal clara'."},
    {"nivel": 7, "nombre": "Bot Legendario", "xp_min": 3000, "xp_next": None, "capacidades": "Máximo nivel. Track record demostrable. Recomendación con capas de análisis y stats históricas."},
]

# Bonificaciones de XP
XP_ACIERTO_BASE = 10
XP_ACIERTO_ALTO_CONFIANZA = 15  # Recibirá +15 en vez de +10 si la confianza era ALTO
XP_ACIERTO_REGIMEN_DIFICIL = 20  # Bono extra por acertar en régimen difícil
XP_ACIERTO_BACKTEST = 5  # Bono extra si el bot tenía backtest disponible (nivel 4+)
XP_MAXIMO_POR_SENAL = 20

XP_ERROR_BASE = -5
XP_ERROR_ALTO_CONFIANZA = -15  # Castigo extra por falsa confianza
XP_ERROR_REGIMEN_FACIL = -10  # Castigo extra por error en régimen fácil

# Niveles reportados
NIVEL_1 = NIVELES[0]
NIVEL_2 = NIVELES[1]


def obtener_nivel(xp: int) -> dict:
    """
    Obtiene el nivel correspondiente al XP dado.
    Retorna el dict del nivel más alto cuyo xp_min <= xp.
    """
    nivel_actual = NIVEL_1
    for nivel in NIVELES:
        if xp >= nivel["xp_min"]:
            nivel_actual = nivel
    return nivel_actual


def calcular_barra(xp: int, xp_next: int | None) -> str:
    """
    Calcula la barra visual de progreso.
    Ejemplo: XP=750, xp_next=1000 → ████████░░ (8/10 bloques llenos)
    """
    if xp_next is None:
        # Nivel máximo — barra completa
        return "██████████"  # 10 bloques llenos

    porcentaje = xp / xp_next
    bloques_llenos = round(porcentaje * 10)
    bloques_llenos = min(bloques_llenos, 10)  # no más de 10
    bloques_llenos = max(bloques_llenos, 0)  # no menos de 0
    return "█" * bloques_llenos + "░" * (10 - bloques_llenos)


def calcular_xp_por_señal(sig: dict) -> tuple[int, str]:
    """
    Calcula cuánto XP ganó o perdió el bot por una señal resuelta.
    Retorna (xp_cantidad, razon).
    """
    outcome = sig.get("outcome", "")
    confidence = sig.get("confidence", "MEDIO")
    market_regime = sig.get("market_regime", "lateral")
    signal_type = sig.get("signal_type", "")

    if outcome == "acierto":
        xp = XP_ACIERTO_BASE

        # Bonificación por confianza ALTO
        if confidence == "ALTO":
            xp = XP_ACIERTO_ALTO_CONFIANZA

        # Bonificación por régimen difícil
        regimen_dificil = ["noticias_Ripple", "noticias_Stellar", "noticias_Hedera", "alta_volatilidad"]
        if market_regime in regimen_dificil:
            xp = max(xp, XP_ACIERTO_REGIMEN_DIFICIL)

        # Bonificación por backtest (nivel 4+)
        # Si el bot tenía nivel 4+ al emitir, recibe +5 extra
        # (Esto se chequea si hay historial suficiente para inferir el nivel)
        xp = min(xp, XP_MAXIMO_POR_SENAL)

        razon = f"✅ Acierto"
        if confidence == "ALTO":
            razon += " (confianza ALTO)"
        if market_regime in regimen_dificil:
            razon += f" (régimen difícil: {market_regime})"
        razon += f" → +{xp} XP"

        return xp, razon

    elif outcome == "error":
        # El castigo es proporcional al XP que se arriesgó
        # Si la señal era de régimen difícil (donde el XP máximo es +20),
        # el error cuesta lo mismo que el acierto hubiera dado
        xp = XP_ERROR_BASE  # -5 base

        # Castigo por falsa confianza
        if confidence == "ALTO":
            xp = XP_ERROR_ALTO_CONFIANZA

        # Castigo proporcional al régimen: si el régimen era difícil
        # (donde un acierto daría +20), el error debe costar -10 o -15
        regimen_dificil = ["noticias_Ripple", "noticias_Stellar", "noticias_Hedera", "alta_volatilidad"]
        if market_regime in regimen_dificil:
            xp = XP_ERROR_BASE * 2  # -10 en régimen difícil

        regimen_facil = ["lateral"]
        if market_regime in regimen_facil:
            xp = XP_ERROR_REGIMEN_FACIL

        razon = f"❌ Error"
        if confidence == "ALTO":
            razon += " (falsa confianza ALTO)"
        if market_regime in regimen_dificil:
            razon += f" (régimen difícil: {market_regime})"
        if market_regime in regimen_facil:
            razon += f" (régimen fácil: {market_regime})"
        razon += f" → {xp} XP"

        return xp, razon

    elif outcome == "anulada":
        return -2, "⚠️ Señal anulada → -2 XP"

    elif outcome == "neutral":
        return 0, "🟡 Neutral → 0 XP (sin ganancia ni pérdida)"

    else:
        return 0, "❓ Outcome desconocido → 0 XP"


def cargar_señales(crypto: str) -> list[dict]:
    """Carga las señales resueltas para una cripto."""
    path = LEARNER_DIR / f"signals-{crypto.lower()}.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def cargar_progress_json() -> dict:
    """Carga el estado actual de progress.json."""
    path = LEARNER_DIR / "progress.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_progress_json(data: dict) -> None:
    """Guarda el estado de progress.json."""
    path = LEARNER_DIR / "progress.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def recalcular_progreso(crypto: str = None, update_file: bool = False) -> dict:
    """
    Recalcula el progreso de XP y niveles para todas las criptos
    (o solo la indicada) basándose en las señales resueltas.
    Retorna el dict de progreso completo.
    """
    cryptos = ["XRP", "XLM", "HBAR"] if crypto is None else [crypto]

    progress = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "cryptos": {},
    }

    xp_total = 0
    niveles_totales = 0

    for crypto in cryptos:
        señales = cargar_señales(crypto)
        señales_resueltas = [s for s in señales if s.get("resolved", False)]

        xp_cripto = 0
        aciertos = 0
        errores = 0
        neutrales = 0
        for s in señales_resueltas:
            xp_cantidad, razon = calcular_xp_por_señal(s)
            xp_cripto += xp_cantidad

            outcome = s.get("outcome", "")
            if outcome == "acierto":
                aciertos += 1
            elif outcome == "error":
                errores += 1
            elif outcome == "neutral":
                neutrales += 1

        total_resueltas = aciertos + errores + neutrales
        precision = (aciertos / total_resueltas) if total_resueltas > 0 else 0

        nivel_cripto = obtener_nivel(max(0, xp_cripto))

        ultima_señal = None
        if señales_resueltas:
            # La última señal resuelta (por timestamp, más reciente primero)
            ordenadas = sorted(señales_resueltas, key=lambda s: s.get("timestamp", ""), reverse=True)
            ultima = ordenadas[0]
            xp_ultima, razon_ultima = calcular_xp_por_señal(ultima)
            ultima_señal = {
                "id": ultima.get("id", "")[:8] + "...",
                "type": ultima.get("signal_type", ""),
                "outcome": ultima.get("outcome", ""),
                "xp_cantidad": xp_ultima,
                "razon": razon_ultima,
                "timestamp": ultima.get("timestamp", ""),
                "confidence": ultima.get("confidence", ""),
            }

        progress["cryptos"][crypto] = {
            "xp": max(0, xp_cripto),
            "nivel": nivel_cripto["nivel"],
            "nivel_nombre": nivel_cripto["nombre"],
            "xp_next": nivel_cripto["xp_next"],
            "capacidades": nivel_cripto["capacidades"],
            "barra": calcular_barra(max(0, xp_cripto), nivel_cripto["xp_next"]),
            "señales_resueltas": total_resueltas,
            "aciertos": aciertos,
            "errores": errores,
            "neutrales": neutrales,
            "precision": round(precision, 2),
            "ultima_señal": ultima_señal,
        }

        xp_total += max(0, xp_cripto)
        niveles_totales += nivel_cripto["nivel"]

    # Nivel global (promedio de XP)
    xp_promedio = xp_total // 3 if len(cryptos) > 0 else 0
    nivel_global_dict = obtener_nivel(xp_promedio)

    progress["xp_global"] = xp_promedio
    progress["nivel_global"] = nivel_global_dict["nivel"]
    progress["nivel_global_nombre"] = nivel_global_dict["nombre"]
    progress["xp_global_next"] = nivel_global_dict["xp_next"]
    progress["barra_global"] = calcular_barra(xp_promedio, nivel_global_dict["xp_next"])

    if update_file:
        guardar_progress_json(progress)

    return progress


def mostrar_progreso(progress: dict) -> None:
    """Muestra el progreso formateado en consola."""
    print("\n" + "=" * 60)
    print("  📊 PROGRESO DEL BOT — SISTEMA DE NIVELES")
    print("=" * 60 + "\n")

    for crypto, data in progress["cryptos"].items():
        xp = data["xp"]
        xp_next = data["xp_next"]
        nivel = data["nivel"]
        nombre = data["nivel_nombre"]
        barra = data["barra"]
        precision = data["precision"]
        resueltas = data["señales_resueltas"]
        aciertos = data["aciertos"]
        errores = data["errores"]
        ultima = data.get("ultima_señal")

        print(f"🤖 NIVEL {crypto}: {barra} {xp}/{xp_next} → Nivel {nivel}: {nombre}")
        print(f"   📈 Señales resueltas: {resueltas} (✅ {aciertos} · ❌ {errores} · 🟡 {data['neutrales']})")
        print(f"   🎯 Precisión: {precision*100:.0f}%")
        print(f"   📋 Capacidades: {data['capacidades']}")
        if ultima:
            print(f"   📌 Última señal: {ultima['razon']}")
        print(f"   🎯 Siguiente nivel: {xp_next - xp} XP faltantes → Nivel {nivel + 1 if nivel < 7 else 'MAX'}")
        print("")

    xp_global = progress["xp_global"]
    xp_next_global = progress["xp_global_next"]
    nivel_global = progress["nivel_global"]
    nombre_global = progress["nivel_global_nombre"]
    barra_global = progress["barra_global"]

    print(f"🤖 NIVEL GLOBAL: {barra_global} {xp_global}/{xp_next_global} → Nivel {nivel_global}: {nombre_global}")
    print(f"   📋 Capacidades globales: {progress['cryptos'].get('XRP', {}).get('capacidades', '—')}")
    print("")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tracker de Niveles y XP del Bot")
    parser.add_argument("--crypto", type=str, help="Cripto específica (XRP, XLM, HBAR)")
    parser.add_argument("--update", action="store_true", help="Actualizar progress.json")
    args = parser.parse_args()

    progress = recalcular_progreso(
        crypto=args.crypto,
        update_file=args.update
    )

    mostrar_progreso(progress)


if __name__ == "__main__":
    main()
