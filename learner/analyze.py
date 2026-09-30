#!/usr/bin/env python3
"""
Analizador de señales cripto — Learner System

Procesa los archivos signals-<crypto>.json, calcula estadísticas
por tipo de señal, por nivel de confianza, y genera reportes que
pueden usarse para actualizar los perfiles de los especialistas.

Uso:
    python analyze.py                    # análisis completo
    python analyze.py --crypto XRP       # solo XRP
    python analyze.py --resolve          # también resuelve señales pendientes
    python analyze.py --update-profiles # actualiza los archivos specialist-*.md
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


def load_signals(crypto: str) -> list[dict]:
    """Carga el historial de señales para una cripto."""
    path = LEARNER_DIR / f"signals-{crypto.lower()}.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_pending_signals(crypto: str, current_price: float) -> list[dict]:
    """
    Resuelve señales pendientes para una cripto dado el precio actual.
    Devuelve las señales que fueron resueltas.
    """
    signals = load_signals(crypto)
    now = datetime.now(timezone.utc)
    resolved = []

    for sig in signals:
        if sig.get("resolved", False):
            continue
        resolve_by = sig.get("resolve_by")
        if not resolve_by:
            continue
        try:
            resolve_dt = datetime.fromisoformat(resolve_by.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue

        if resolve_dt > now:
            continue  # aún no es hora

        # Determinar outcome
        price_at_signal = sig.get("price_at_signal", 0)
        direction = sig.get("direction", "NEUTRO")
        signal_type = sig.get("signal_type", "")
        horizon = sig.get("horizon_hours", 24)

        if price_at_signal and current_price:
            change_pct = ((current_price - price_at_signal) / price_at_signal) * 100
        else:
            change_pct = 0

        outcome = determine_outcome(signal_type, direction, change_pct)
        sig["resolved"] = True
        sig["outcome"] = outcome
        sig["price_at_resolution"] = current_price
        sig["price_change_pct"] = round(change_pct, 2)
        sig["outcome_detail"] = (
            f"Cambio: {change_pct:+.2f}% desde {price_at_signal} a {current_price}"
        )
        resolved.append(sig)

    # Guardar cambios
    if resolved:
        with open(LEARNER_DIR / f"signals-{crypto.lower()}.json", "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)

    return resolved


def determine_outcome(signal_type: str, direction: str, change_pct: float) -> str:
    """
    Determina si una señal fue acierto, error o neutral basado en el cambio %.
    Los umbrales son configurable por tipo de señal.
    """
    # Umbrales por defecto (pueden refinarse)
    thresholds = {
        "rsi_overbought_reversal": {"acierto": -2.0, "neutral": -2.0},
        "rsi_oversold_rebound": {"acierto": 2.0, "neutral": 2.0},
        "macd_bullish_cross": {"acierto": 0.5, "neutral": 0.5},
        "macd_bearish_cross": {"acierto": -0.5, "neutral": -0.5},
        "support_breakdown": {"acierto": -1.0, "neutral": 1.0},
        "resistance_breakout": {"acierto": 1.0, "neutral": 1.0},
        "news_positive_impact": {"acierto": 1.5, "neutral": 1.5},
        "news_negative_impact": {"acierto": -1.5, "neutral": 1.5},
        "sentiment_shift": {"acierto": 1.0, "neutral": 1.0},
        "fear_greed_extreme": {"acierto": -3.0, "neutral": 3.0},
        "whale_accumulation": {"acierto": -2.0, "neutral": 2.0},
    }

    th = thresholds.get(signal_type, {"acierto": 1.0, "neutral": 1.0})

    if direction == "ALCISTA":
        if change_pct >= th["acierto"]:
            return "acierto"
        elif abs(change_pct) < th["neutral"]:
            return "neutral"
        else:
            return "error"
    elif direction == "BAJISTA":
        if change_pct <= th["acierto"]:
            return "acierto"
        elif abs(change_pct) < th["neutral"]:
            return "neutral"
        else:
            return "error"
    else:
        # NEUTRO: no hay predicción direccional clara
        if abs(change_pct) < th["neutral"]:
            return "neutral"
        else:
            return "neutral"  # neutral es el default para señales neutras


def compute_statistics(signals: list[dict]) -> dict:
    """
    Calcula estadísticas detalladas para un conjunto de señales.
    """
    stats = {
        "total": len(signals),
        "resolved": sum(1 for s in signals if s.get("resolved")),
        "pendientes": sum(1 for s in signals if not s.get("resolved")),
        "by_type": defaultdict(lambda: {"total": 0, "aciertos": 0, "errores": 0, "neutrales": 0}),
        "by_confidence": defaultdict(lambda: {"total": 0, "aciertos": 0, "errores": 0}),
        "by_direction": defaultdict(lambda: {"total": 0, "aciertos": 0, "errores": 0}),
        "recent_10": {"aciertos": 0, "errores": 0, "neutrales": 0, "total": 0},
    }

    resolved_signals = [s for s in signals if s.get("resolved")]

    for sig in resolved_signals:
        stype = sig.get("signal_type", "unknown")
        conf = sig.get("confidence", "MEDIO")
        direction = sig.get("direction", "NEUTRO")
        outcome = sig.get("outcome", "pendiente")

        # Por tipo
        stats["by_type"][stype]["total"] += 1
        if outcome == "acierto":
            stats["by_type"][stype]["aciertos"] += 1
        elif outcome == "error":
            stats["by_type"][stype]["errores"] += 1
        elif outcome == "neutral":
            stats["by_type"][stype]["neutrales"] += 1

        # Por confianza
        stats["by_confidence"][conf]["total"] += 1
        if outcome == "acierto":
            stats["by_confidence"][conf]["aciertos"] += 1
        elif outcome == "error":
            stats["by_confidence"][conf]["errores"] += 1

        # Por dirección
        stats["by_direction"][direction]["total"] += 1
        if outcome == "acierto":
            stats["by_direction"][direction]["aciertos"] += 1
        elif outcome == "error":
            stats["by_direction"][direction]["errores"] += 1

    # Últimas 10 señales resueltas (más recientes)
    recent = sorted(resolved_signals, key=lambda s: s.get("timestamp", ""), reverse=True)[:10]
    stats["recent_10"]["total"] = len(recent)
    for sig in recent:
        outcome = sig.get("outcome", "pendiente")
        if outcome == "acierto":
            stats["recent_10"]["aciertos"] += 1
        elif outcome == "error":
            stats["recent_10"]["errores"] += 1
        elif outcome == "neutral":
            stats["recent_10"]["neutrales"] += 1

    # Convertir defaultdicts a dicts normales para serialización
    stats["by_type"] = dict(stats["by_type"])
    stats["by_confidence"] = dict(stats["by_confidence"])
    stats["by_direction"] = dict(stats["by_direction"])

    return stats


def format_stats_summary(stats: dict) -> str:
    """Genera un resumen legible de las estadísticas."""
    lines = []
    lines.append(f"📊 RESUMEN ESTADÍSTICO")
    lines.append(f"   Total de señales: {stats['total']}")
    lines.append(f"   Resueltas: {stats['resolved']}")
    lines.append(f"   Pendientes: {stats['pendientes']}")
    lines.append("")

    if stats["resolved"] == 0:
        lines.append("   ⚠️  No hay señales resueltas todavía — el perfil opera con hipótesis prior.")
        return "\n".join(lines)

    # Por tipo de señal
    lines.append("📈 POR TIPO DE SEÑAL")
    for stype, data in sorted(stats["by_type"].items()):
        total = data["total"]
        aciertos = data["aciertos"]
        precision = (aciertos / total * 100) if total > 0 else 0
        lines.append(f"   {stype}: {aciertos}/{total} ({precision:.0f}%)")
    lines.append("")

    # Por confianza
    lines.append("🎯 POR NIVEL DE CONFIANZA")
    for conf, data in sorted(stats["by_confidence"].items()):
        total = data["total"]
        aciertos = data["aciertos"]
        precision = (aciertos / total * 100) if total > 0 else 0
        lines.append(f"   {conf}: {aciertos}/{total} ({precision:.0f}%)")
    lines.append("")

    # Por dirección
    lines.append("🧭 POR DIRECCIÓN")
    for direction, data in sorted(stats["by_direction"].items()):
        total = data["total"]
        aciertos = data["aciertos"]
        precision = (aciertos / total * 100) if total > 0 else 0
        lines.append(f"   {direction}: {aciertos}/{total} ({precision:.0f}%)")
    lines.append("")

    # Últimas 10
    recent = stats["recent_10"]
    lines.append("🔍 ÚLTIMAS 10 SEÑALES RESUELTAS")
    lines.append(f"   Aciertos: {recent['aciertos']}/{recent['total']} ({recent['aciertos']/recent['total']*100:.0f}%)" if recent['total'] > 0 else "   Sin data")
    lines.append("")

    return "\n".join(lines)


def update_profile(crypto: str, stats: dict) -> None:
    """
    Actualiza el perfil del especialista con las nuevas estadísticas.
    Lee el archivo actual, reemplaza las secciones de estadísticas,
    y guarda.
    """
    profile_path = LEARNER_DIR / f"specialist-{crypto.lower()}.md"
    if not profile_path.exists():
        print(f"⚠️  Perfil no encontrado: {profile_path}")
        return

    with open(profile_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Reemplazar tabla de estadísticas por tipo
    new_type_table = format_type_table(stats["by_type"])
    content = replace_between(content, "## Estadísticas por Tipo de Señal", "## Estadísticas por Nivel de Confianza", new_type_table)

    # Reemplazar tabla de confianza
    new_conf_table = format_confidence_table(stats["by_confidence"])
    content = replace_between(content, "## Estadísticas por Nivel de Confianza", "## Régimen de Mercado Actual", new_conf_table)

    # Actualizar fecha de última actualización
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # Buscar y reemplazar la línea de "Última actualización: ..."
    import re
    content = re.sub(
        r"Última actualización:.*",
        f"Última actualización: {now_str}",
        content
    )

    with open(profile_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Perfil {crypto} actualizado: {profile_path}")


def format_type_table(by_type: dict) -> str:
    """Formatea la tabla de estadísticas por tipo de señal en markdown."""
    lines = [
        "| Tipo de Señal | Aciertos / Total | Precisión | Notas |",
        "|---------------|------------------|-----------|-------|",
    ]
    for stype, data in sorted(by_type.items()):
        total = data["total"]
        aciertos = data["aciertos"]
        precision = f"{(aciertos / total * 100):.0f}%" if total > 0 else "insuficiente data"
        notes = data.get("notes", "")
        lines.append(f"| {stype} | {aciertos} / {total} | {precision} | {notes} |")
    return "\n".join(lines)


def format_confidence_table(by_conf: dict) -> str:
    """Formatea la tabla de estadísticas por confianza en markdown."""
    lines = [
        "| Nivel de Confianza | Aciertos / Total | Precisión |",
        "|--------------------|------------------|-----------|",
    ]
    for conf, data in sorted(by_conf.items()):
        total = data["total"]
        aciertos = data["aciertos"]
        precision = f"{(aciertos / total * 100):.0f}%" if total > 0 else "insuficiente data"
        lines.append(f"| {conf} | {aciertos} / {total} | {precision} |")
    return "\n".join(lines)


def replace_between(text: str, start_marker: str, end_marker: str, new_content: str) -> str:
    """
    Reemplaza el contenido entre dos marcadores en un texto.
    Si los marcadores no existen, devuelve el texto original.
    """
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return text

    end_idx = text.find(end_marker, start_idx)
    if end_idx == -1:
        # Si no hay end_marker, reemplazar hasta el final
        end_idx = len(text)

    # Encontrar el final de la línea del start_marker
    line_end = text.find("\n", start_idx)
    if line_end == -1:
        line_end = start_idx

    # Encontrar el inicio de la línea del end_marker
    line_start = text.rfind("\n", 0, end_idx) + 1

    return text[:line_end + 1] + new_content + "\n\n" + text[line_start:]


def run_analysis(crypto: str = None, resolve: bool = False, update_profiles: bool = False):
    """Ejecuta el análisis completo."""
    cryptos = ["XRP", "XLM", "HBAR"] if crypto is None else [crypto]

    for crypto_name in cryptos:
        print(f"\n{'='*60}")
        print(f"  ANALISIS — {crypto_name}")
        print(f"{'='*60}")

        # Resolver señales pendientes si se pidió
        if resolve:
            print("   🔍 Resolviendo señales pendientes...")
            # Obtener precio actual (en producción esto sería una API call)
            # Por ahora, simulamos que el precio se obtiene externamente
            print(f"   ⏳ Se necesita precio actual de {crypto_name} para resolver.")
            print(f"   → Usar --price <valor> o dejar que el proceso externo llene los datos.")

        signals = load_signals(crypto_name)
        stats = compute_statistics(signals)
        summary = format_stats_summary(stats)
        print(summary)

        if update_profiles:
            update_profile(crypto_name, stats)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analizador de señales cripto")
    parser.add_argument("--crypto", type=str, help="Cripto a analizar (XRP, XLM, HBAR)")
    parser.add_argument("--resolve", action="store_true", help="Resolver señales pendientes")
    parser.add_argument("--update-profiles", action="store_true", help="Actualizar archivos specialist-*.md")
    parser.add_argument("--price", type=float, help="Precio actual para resolver señales")
    args = parser.parse_args()

    run_analysis(
        crypto=args.crypto,
        resolve=args.resolve,
        update_profiles=args.update_profiles,
    )
