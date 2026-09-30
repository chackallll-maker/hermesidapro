#!/usr/bin/env python
"""
Actualiza el perfil del especialista (specialist-*.md) con las estadísticas
de las señales resueltas en signals-*.json.

Para cada cripto:
1. Lee signals-<crypto>.json
2. Calcula estadísticas por tipo de señal y por nivel de confianza
3. Actualiza el archivo specialist-<crypto>.md

No borra hipótesis ni observaciones cualitativas existentes.
Solo actualiza las secciones de estadísticas.

Uso: python update_specialist.py
"""

import json
import re
from pathlib import Path
from collections import defaultdict

PROJECT_DIR = Path("C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor")
CRYPTO_LIST = ["XRP", "XLM", "HBAR"]


def load_signals(crypto: str) -> list:
    """Cargar señales de un crypto."""
    signals_file = PROJECT_DIR / "learner" / f"signals-{crypto.lower()}.json"
    if not signals_file.exists():
        return []
    with open(signals_file, "r") as f:
        return json.load(f)


def compute_stats(signals: list) -> dict:
    """
    Calcular estadísticas por tipo de señal y por nivel de confianza.
    Solo considera señales resueltas (resolved=true).
    """
    by_type = defaultdict(lambda: {"aciertos": 0, "total": 0})
    by_confidence = defaultdict(lambda: {"aciertos": 0, "total": 0})

    for s in signals:
        if not s.get("resolved", False):
            continue

        outcome = s.get("outcome", "pendiente")
        signal_type = s.get("signal_type", "unknown")
        confidence = s.get("confidence", "BAJO")

        # Por tipo de señal
        by_type[signal_type]["total"] += 1
        if outcome == "acierto":
            by_type[signal_type]["aciertos"] += 1

        # Por nivel de confianza
        by_confidence[confidence]["total"] += 1
        if outcome == "acierto":
            by_confidence[confidence]["aciertos"] += 1

    return {
        "by_type": dict(by_type),
        "by_confidence": dict(by_confidence),
    }


def generate_stats_table(stats: dict, include_notes: bool = True) -> str:
    """Generar tabla de estadísticas por tipo de señal."""
    if not stats["by_type"]:
        return "|| Tipo de Señal | Aciertos / Total | Precisión | Notas |\n||---------------|------------------|-----------|-------|\n|| *(sin datos)* | — | — | |"

    lines = ["|| Tipo de Señal | Aciertos / Total | Precisión | Notas |"]
    lines.append("||---------------|------------------|-----------|-------|")

    for sig_type, data in sorted(stats["by_type"].items()):
        aciertos = data["aciertos"]
        total = data["total"]
        precision = (aciertos / total * 100) if total > 0 else 0
        notes = ""
        if precision == 0:
            notes = "esperando más data"
        elif precision < 50:
            notes = "baja precisión — calibrar"
        elif precision >= 70:
            notes = "confiable"
        lines.append(f"| {sig_type} | {aciertos} / {total} | {precision:.0f}% | {notes} |")

    return "\n".join(lines)


def generate_confidence_table(stats: dict) -> str:
    """Generar tabla de estadísticas por nivel de confianza."""
    if not stats["by_confidence"]:
        return "|| Nivel de Confianza | Aciertos / Total | Precisión |\n|--------------------|------------------|-----------|\n|| *(sin datos)* | — | — |"

    lines = ["|| Nivel de Confianza | Aciertos / Total | Precisión |"]
    lines.append("|--------------------|------------------|-----------|")

    for conf in ["ALTO", "MEDIO", "BAJO"]:
        data = stats["by_confidence"].get(conf, {"aciertos": 0, "total": 0})
        aciertos = data["aciertos"]
        total = data["total"]
        precision = (aciertos / total * 100) if total > 0 else 0
        if total == 0:
            lines.append(f"| {conf} | *(sin datos)* | — |")
        else:
            lines.append(f"| {conf} | {aciertos} / {total} | {precision:.0f}% |")

    return "\n".join(lines)


def update_specialist_file(crypto: str, stats: dict):
    """Actualizar el archivo specialist-<crypto>.md con las nuevas estadísticas."""
    specialist_file = PROJECT_DIR / "learner" / f"specialist-{crypto.lower()}.md"

    if not specialist_file.exists():
        print(f"⚠️  No existe {specialist_file.name} — saltando")
        return

    content = specialist_file.read_text()

    # Generar las nuevas tablas
    new_type_table = generate_stats_table(stats)
    new_conf_table = generate_confidence_table(stats)

    # Buscar y reemplazar la sección de estadísticas por tipo de señal
    # Patrón: desde "## Estadísticas por Tipo de Señal" hasta la siguiente "## "
    pattern_type = r'(## Estadísticas por Tipo de Señal\n)(.*?)(?=\n## )'
    match_type = re.search(pattern_type, content, re.DOTALL)

    if match_type:
        old_section = match_type.group(0)
        new_section = f"## Estadísticas por Tipo de Señal\n{new_type_table}"
        content = content.replace(old_section, new_section)
        print(f"  ✅ Actualizada tabla de estadísticas por tipo para {crypto}")
    else:
        print(f"  ⚠️  No encontré sección de estadísticas por tipo en {crypto} — ignorando")

    # Buscar y reemplazar la sección de estadísticas por confianza
    pattern_conf = r'(## Estadísticas por Nivel de Confianza.*?\n)(.*?)(?=\n## )'
    match_conf = re.search(pattern_conf, content, re.DOTALL)

    if match_conf:
        old_section = match_conf.group(0)
        new_section = f"## Estadísticas por Nivel de Confianza\n{new_conf_table}"
        content = content.replace(old_section, new_section)
        print(f"  ✅ Actualizada tabla de estadísticas por confianza para {crypto}")
    else:
        print(f"  ⚠️  No encontré sección de estadísticas por confianza en {crypto} — ignorando")

    # Actualizar fecha de última actualización
    now_utc = f"Última actualización: {Path(__file__).parent.name}"  # placeholder, usamos la fecha real abajo
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    content = re.sub(
        r'Última actualización: \d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC',
        f'Última actualización: {now}',
        content
    )

    specialist_file.write_text(content)


def update_all_specialists():
    """Actualizar todos los perfiles de especialistas."""
    for crypto in CRYPTO_LIST:
        print(f"\n📊 Actualizando especialista {crypto}...")
        signals = load_signals(crypto)
        resolved = [s for s in signals if s.get("resolved", False)]
        print(f"  Señales resueltas encontradas: {len(resolved)}")

        if not resolved:
            print(f"  ✅ {crypto}: no hay señales resueltas para actualizar")
            continue

        stats = compute_stats(signals)
        print(f"  Tipos de señal con data: {list(stats['by_type'].keys())}")
        print(f"  Total aciertos: {sum(d['aciertos'] for d in stats['by_type'].values())} / "
              f"{sum(d['total'] for d in stats['by_type'].values())}")

        update_specialist_file(crypto, stats)


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 Actualizando perfiles de especialistas")
    print("=" * 60)
    update_all_specialists()
    print("\n✅ Terminado.")
