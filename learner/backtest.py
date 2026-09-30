#!/usr/bin/env python3
"""
Backtester del sistema de señales cripto — Crypto Monitor Learner

Descarga velas históricas de Binance (OHLCV), calcula indicadores
técnicos reales (RSI, MACD, SMA) y simula las reglas del bot para
medir qué tan preciso hubiera sido cada tipo de señal en el histórico.

No modifica nada del sistema en vivo. Solo produce un reporte de
estadísticas pasadas para calibrar el learner antes de usar en vivo.

Uso:
    python backtest.py                          # Backtest completo (XRP, XLM, HBAR)
    python backtest.py --crypto XRP             # Solo XRP
    python backtest.py --since 90              # Últimos 90 días (por defecto 90)
    python backtest.py --output stats.md        # Guarda reporte en archivo
"""

import json
import sys
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

BASE_DIR = Path(__file__).parent.parent
LEARNER_DIR = BASE_DIR / "learner"

# Headers para Binance API
HEADERS = {"User-Agent": "CryptoLearner/1.0"}

# Mapeo de cripto → par Binance
BINANCE_PAIRS = {
    "XRP": "XRPUSDT",
    "XLM": "XLMUSDT",
    "HBAR": "HBARUSDT",
}

# IDs de CoinGecko para mostrar nombre
COINGECKO_IDS = {
    "XRP": "ripple",
    "XLM": "stellar",
    "HBAR": "hedera-hashgraph",
}


def fetch_ohlcv(symbol: str, interval: str, limit: int) -> list[list]:
    """
    Descarga velas OHLCV de Binance.
    symbol: ej. 'XRPUSDT'
    interval: '1h', '4h', '1d'
    limit: máx 1000 para 1h, 200 para 1d en la API pública
    Retorna lista de [timestamp, open, high, low, close, volume]
    """
    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval={interval}&limit={limit}"
    )
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Binance devuelve strings, convertimos a float
            return [
                [int(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])]
                for row in data
            ]
    except (URLError, HTTPError, json.JSONDecodeError, ValueError, IndexError) as e:
        print(f"   ⚠️  Error descargando {symbol} {interval}: {e}")
        return []


def rsi(closes: list[float], period: int = 14) -> float | None:
    """
    Calcula RSI(period) a partir de lista de closes.
    Retorna el último valor calculado o None si hay pocos datos.
    """
    if len(closes) < period + 1:
        return None

    gains = []
    losses = []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(abs(min(diff, 0)))

    # Promedio inicial (simple)
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100.0

    # Wilder's smoothing para el resto
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi_value = 100 - (100 / (1 + rs))
    return round(rsi_value, 2)


def macd(closes: list[float], fast: int = 12, slow: int = 26, signal: int = 9) -> dict | None:
    """
    Calcula MACD: línea MACD, línea de señal, histograma.
    Retorna dict con los últimos valores o None si hay pocos datos.
    """
    if len(closes) < slow + signal:
        return None

    def ema(data, period):
        if len(data) < period:
            return None
        multiplier = 2 / (period + 1)
        ema_values = [sum(data[:period]) / period]
        for i in range(period, len(data)):
            ema_values.append((data[i] - ema_values[-1]) * multiplier + ema_values[-1])
        return ema_values

    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)

    if ema_fast is None or ema_slow is None:
        return None

    # Alinear longitudes (EMA slow es más corta)
    diff = len(ema_fast) - len(ema_slow)
    ema_fast = ema_fast[diff:]

    macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
    macd_signal = ema(macd_line, signal)

    if macd_signal is None or len(macd_signal) < 1:
        return None

    macd_histogram = [m - s for m, s in zip(macd_line[-len(macd_signal):], macd_signal)]

    return {
        "macd": round(macd_line[-1], 4),
        "signal": round(macd_signal[-1], 4),
        "histogram": round(macd_histogram[-1], 4),
        "macd_prev": round(macd_line[-2], 4) if len(macd_line) > 1 else None,
    }


def sma(closes: list[float], period: int) -> float | None:
    """Calcula SMA(period) — último valor."""
    if len(closes) < period:
        return None
    return round(sum(closes[-period:]) / period, 2)


def classify_trend(price: float, sma_50: float | None, sma_200: float | None) -> str:
    """Clasifica la tendencia basada en precios vs SMAs."""
    if sma_50 is not None and sma_200 is not None:
        if price > sma_50 and sma_50 > sma_200:
            return "ALCISTA FUERTE"
        elif price > sma_50:
            return "ALCISTA"
        elif price < sma_50 and sma_50 < sma_200:
            return "BAJISTA FUERTE"
        elif price < sma_50:
            return "BAJISTA"
        else:
            return "LATERAL"
    elif sma_50 is not None:
        if price > sma_50:
            return "ALCISTA"
        else:
            return "BAJISTA"
    return "LATERAL"


def simulate_signal(
    signal_type: str,
    timestamp: int,
    closes: list[float],
    volumes: list[float],
    rsi_val: float | None,
    macd_data: dict | None,
    sma_50: float | None,
    sma_200: float | None,
    price_at_signal: float,
    direction: str,
    horizon_hours: int,
    interval_hours: int,
) -> str:
    """
    Simula si una señal hubiera acertado.
    Retorna 'acierto', 'error', 'neutral' o 'insuficiente_data'.
    """
    idx = len(closes) - 1  # índice de la vela más reciente simulada

    # Buscar el índice de resolución (horizon_hours después)
    steps_ahead = horizon_hours // interval_hours
    if steps_ahead < 1 or idx + steps_ahead >= len(closes):
        return "insuficiente_data"

    price_at_resolution = closes[idx + steps_ahead]
    change_pct = ((price_at_resolution - price_at_signal) / price_at_signal) * 100

    # Criterios de acierto por tipo de señal (mismos que en resolve.py)
    thresholds = {
        "rsi_overbought_reversal": {"acierto_dir": "BAJISTA", "min_change": -2.0},
        "rsi_oversold_rebound": {"acierto_dir": "ALCISTA", "min_change": 2.0},
        "macd_bullish_cross": {"acierto_dir": "ALCISTA", "min_change": 0.5},
        "macd_bearish_cross": {"acierto_dir": "BAJISTA", "min_change": -0.5},
        "support_breakdown": {"acierto_dir": "BAJISTA", "min_change": -1.0},
        "resistance_breakout": {"acierto_dir": "ALCISTA", "min_change": 1.0},
        "news_positive_impact": {"acierto_dir": "ALCISTA", "min_change": 1.5},
        "news_negative_impact": {"acierto_dir": "BAJISTA", "min_change": -1.5},
    }

    config = thresholds.get(signal_type, None)
    if config is None:
        return "neutral"

    if direction == config["acierto_dir"] and abs(change_pct) >= abs(config["min_change"]):
        return "acierto"
    elif abs(change_pct) < abs(config["min_change"]) * 0.5:
        return "neutral"
    else:
        return "error"


def backtest_crypto(crypto: str, days: int = 90, interval_hours: int = 1) -> dict:
    """
    Ejecuta el backtest para una cripto.
    Retorna estadísticas por tipo de señal.
    """
    symbol = BINANCE_PAIRS.get(crypto)
    if not symbol:
        return {"error": f"Pair no encontrada para {crypto}"}

    # Descargar datos 1h (más granular para backtest)
    # 90 días × 24h = 2160 velas 1h
    max_limit = 1000
    limit = min(max_limit, days * 24)
    klines_1h = fetch_ohlcv(symbol, "1h", limit)

    if not klines_1h:
        return {"error": f"No se pudieron descargar datos de {symbol}"}

    closes_1h = [k[4] for k in klines_1h]
    volumes_1h = [k[5] for k in klines_1h]
    timestamps_1h = [k[0] for k in klines_1h]

    # Descargar datos 1d para SMA 200
    klines_1d = fetch_ohlcv(symbol, "1d", min(200, days + 200))
    closes_1d = [k[4] for k in klines_1d] if klines_1d else []

    results = {
        "total_vegas_disponibles": len(closes_1h),
        "crypto": crypto,
        "days_analizados": days,
        "by_signal": {},
        "summary": {},
    }

    # Simular todas las ventanas posibles (cada vela es un punto de señal potencial)
    # Para no ser demasiado lento, usamos cada 24 velas (cada día) como punto de evaluación
    step = 24 if interval_hours == 1 else 1

    for idx in range(MIN_VELAS_RSI, len(closes_1h) - MAX_HORIZON_STEPS, step):
        # Datos hasta este punto
        closes_window = closes_1h[:idx + 1]
        rsi_val = rsi(closes_window, 14)
        macd_data = macd(closes_window, 12, 26, 9)
        sma_50 = sma(closes_1h[:idx + 1], 50) if idx >= 49 else None
        sma_200 = sma(closes_1d[:idx // 24 + 1], 200) if idx >= 24 * 199 else None
        price_at_signal = closes_1h[idx]
        timestamp = timestamps_1h[idx]

        # Determinar régimen de mercado (tendencia vs lateral)
        if sma_50 is not None and sma_200 is not None:
            if price_at_signal > sma_50 and sma_50 > sma_200:
                regime = "tendencia_alcista"
            elif price_at_signal < sma_50 and sma_50 < sma_200:
                regime = "tendencia_bajista"
            else:
                regime = "lateral"
        else:
            regime = "lateral"

        # Generar señales potenciales basadas en indicadores reales
        signalos_a_probar = []

        # RSI > 70 → señal de sobrecomprado
        if rsi_val is not None and rsi_val > 70:
            signalos_a_probar.append({
                "type": "rsi_overbought_reversal",
                "direction": "BAJISTA",
                "confidence": "ALTO" if rsi_val > 80 else "MEDIO",
                "horizon": 8,
                "price": price_at_signal,
            })

        # RSI < 30 → señal de sobrevendido
        if rsi_val is not None and rsi_val < 30:
            signalos_a_probar.append({
                "type": "rsi_oversold_rebound",
                "direction": "ALCISTA",
                "confidence": "ALTO" if rsi_val < 20 else "MEDIO",
                "horizon": 8,
                "price": price_at_signal,
            })

        # MACD bullish cross
        if macd_data is not None and macd_data.get("macd_prev") is not None:
            if macd_data["macd_prev"] < macd_data["signal"] and macd_data["macd"] >= macd_data["signal"]:
                signalos_a_probar.append({
                    "type": "macd_bullish_cross",
                    "direction": "ALCISTA",
                    "confidence": "MEDIO",
                    "horizon": 24,
                    "price": price_at_signal,
                })
            elif macd_data["macd_prev"] > macd_data["signal"] and macd_data["macd"] <= macd_data["signal"]:
                signalos_a_probar.append({
                    "type": "macd_bearish_cross",
                    "direction": "BAJISTA",
                    "confidence": "MEDIO",
                    "horizon": 24,
                    "price": price_at_signal,
                })

        # Evaluar cada señal simulada
        for sig in signalos_a_probar:
            sig_type = sig["type"]
            if sig_type not in results["by_signal"]:
                results["by_signal"][sig_type] = {
                    "total": 0,
                    "aciertos": 0,
                    "errores": 0,
                    "neutrales": 0,
                    "insuficientes": 0,
                    "by_confidence": {"ALTO": {"total": 0, "aciertos": 0}, "MEDIO": {"total": 0, "aciertos": 0}, "BAJO": {"total": 0, "aciertos": 0}},
                    "by_regime": {},
                }

            outcome = simulate_signal(
                sig_type,
                timestamp,
                closes_1h,
                volumes_1h,
                rsi_val,
                macd_data,
                sma_50,
                sma_200,
                sig["price"],
                sig["direction"],
                sig["horizon"],
                1,  # interval 1h
            )

            results["by_signal"][sig_type]["total"] += 1

            if outcome == "acierto":
                results["by_signal"][sig_type]["aciertos"] += 1
                results["by_signal"][sig_type]["by_confidence"][sig["confidence"]]["total"] += 1
                results["by_signal"][sig_type]["by_confidence"][sig["confidence"]]["aciertos"] += 1
            elif outcome == "error":
                results["by_signal"][sig_type]["errores"] += 1
            elif outcome == "neutral":
                results["by_signal"][sig_type]["neutrales"] += 1
            else:
                results["by_signal"][sig_type]["insuficientes"] += 1

            # By regime
            if regime not in results["by_signal"][sig_type]["by_regime"]:
                results["by_signal"][sig_type]["by_regime"][regime] = {"total": 0, "aciertos": 0}
            results["by_signal"][sig_type]["by_regime"][regime]["total"] += 1
            if outcome == "acierto":
                results["by_signal"][sig_type]["by_regime"][regime]["aciertos"] += 1

    # Calcular resumen
    summary = {}
    total_aciertos = 0
    total_señales = 0
    for sig_type, data in results["by_signal"].items():
        t = data["total"]
        a = data["aciertos"]
        precision = (a / t * 100) if t > 0 else 0
        summary[sig_type] = {
            "total": t,
            "aciertos": a,
            "errores": data["errores"],
            "neutrales": data["neutrales"],
            "insuficientes": data["insuficientes"],
            "precision": round(precision, 1),
        }
        total_aciertos += a
        total_señales += t

    results["summary"] = summary
    results["overall_precision"] = round((total_aciertos / total_señales * 100) if total_señales > 0 else 0, 1)
    results["total_señales"] = total_señales
    results["total_aciertos"] = total_aciertos

    return results


def generate_report(all_results: dict) -> str:
    """Genera un reporte markdown del backtest."""
    lines = []
    lines.append("# Backtest del Sistema de Señales — Reporte")
    lines.append("")
    lines.append(f"*Generado: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append("")
    lines.append("## Resumen Ejecutivo")
    lines.append("")
    lines.append("Este reporte muestra qué tan preciso hubiera sido el sistema de señales")
    lines.append("del bot si hubiera estado operando en el pasado reciente. Los datos son")
    lines.append("calculados desde velas OHLCV reales de Binance (no estimaciones).")
    lines.append("")
    lines.append("Estas estadísticas sirven para calibrar el **learner** antes de usar")
    lines.append("señales en vivo: sabemos qué tipos de señales tienen historical precision")
    lines.append("y podemos ajustar los niveles de confianza en consecuencia.")
    lines.append("")

    for crypto, results in all_results.items():
        if "error" in results:
            lines.append(f"## {crypto} ❌ Error")
            lines.append(f"No se pudieron obtener datos: {results['error']}")
            lines.append("")
            continue

        lines.append(f"## {crypto}")
        lines.append("")
        lines.append(f"- **Datos analizados:** {results['total_vegas_disponibles']} velas 1h ({results['days_analizados']} días)")
        lines.append(f"- **Total de señales simuladas:** {results['total_señales']}")
        lines.append(f"- **Precisión general:** {results['overall_precision']}%")
        lines.append("")

        lines.append("### Por Tipo de Señal")
        lines.append("")
        lines.append("| Tipo de Señal | Total | ✅ Aciertos | ❌ Errores | 🟡 Neutrales | Precisión |")
        lines.append("|---------------|-------|-------------|-----------|-------------|----------|")

        for sig_type, data in sorted(results["summary"].items()):
            t = data["total"]
            a = data["aciertos"]
            e = data["errores"]
            n = data["neutrales"]
            p = data["precision"]
            lines.append(f"| {sig_type} | {t} | {a} | {e} | {n} | {p}% |")

        lines.append("")
        lines.append("### Por Nivel de Confianza (si hay data)")
        lines.append("")

        # Calcular por confianza
        conf_stats = {}
        for sig_type, data in results["by_signal"].items():
            for conf, conf_data in data.get("by_confidence", {}).items():
                if conf not in conf_stats:
                    conf_stats[conf] = {"total": 0, "aciertos": 0}
                conf_stats[conf]["total"] += conf_data["total"]
                conf_stats[conf]["aciertos"] += conf_data["aciertos"]

        if conf_stats:
            for conf in ["ALTO", "MEDIO", "BAJO"]:
                if conf in conf_stats:
                    t = conf_stats[conf]["total"]
                    a = conf_stats[conf]["aciertos"]
                    p = (a / t * 100) if t > 0 else 0
                    lines.append(f"- **{conf}:** {a}/{t} señales ({p:.1f}%)")
        else:
            lines.append("- No hay enough data para estadísticas por confianza.")

        lines.append("")
        lines.append("### Observaciones por Régimen de Mercado")
        lines.append("")

        for sig_type, data in results["by_signal"].items():
            regime_data = data.get("by_regime", {})
            if regime_data:
                lines.append(f"**{sig_type}:**")
                for regime, rd in regime_data.items():
                    t = rd["total"]
                    a = rd["aciertos"]
                    p = (a / t * 100) if t > 0 else 0
                    lines.append(f"-  {regime}: {a}/{t} ({p:.1f}%)")
                lines.append("")

    lines.append("## Cómo Usar Este Reporte")
    lines.append("")
    lines.append("1. Revisar las señales con **baja precisión** (<50%) — estas deben tener confianza baja en vivo")
    lines.append("2. Revisar las señales con **alta precisión** (>70%) — estas pueden tener confianza ALTO")
    lines.append("3. Los perfiles del learner (`specialist-*.md`) deben reflejar estas stats de backtest como")
    lines.append("   conocimiento prior antes de que el learner tenga data propia")
    lines.append("4. Si una señal tiene <30% precision en el backtest, no usarla en vivo hasta que el")
    lines.append("   learner acumule contrara data")

    return "\n".join(lines)


MIN_VELAS_RSI = 15  # mínimo de velas para RSI(14): 14 ganancias + 1
MAX_HORIZON_STEPS = 48  # máximo horizon (48h = 2 días para señales de 24h horizon)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Backtester del sistema de señales cripto")
    parser.add_argument("--crypto", type=str, help="Cripto a backtear (XRP, XLM, HBAR)")
    parser.add_argument("--days", type=int, default=90, help="Días de datos históricos (default: 90)")
    parser.add_argument("--interval", type=int, default=1, help="Intervalo de velas en horas (default: 1h)")
    parser.add_argument("--output", type=str, help="Guardar reporte en archivo .md")
    args = parser.parse_args()

    cryptos = ["XRP", "XLM", "HBAR"] if args.crypto is None else [args.crypto]

    print(f"\n{'='*60}")
    print(f"  BACKTEST — {', '.join(cryptos)} ({args.days} días)")
    print(f"{'='*60}\n")

    all_results = {}

    for crypto in cryptos:
        print(f"🔍 Backteando {crypto}...")
        results = backtest_crypto(crypto, days=args.days, interval_hours=args.interval)
        all_results[crypto] = results

        if "error" in results:
            print(f"   ❌ Error: {results['error']}")
        else:
            print(f"   ✅ {results['total_señales']} señales simuladas")
            print(f"   🎯 Precisión general: {results['overall_precision']}%")
            for sig_type, data in results["summary"].items():
                if data["total"] > 0:
                    print(f"      {sig_type}: {data['aciertos']}/{data['total']} ({data['precision']}%)")
            print("")

    # Generar reporte
    report = generate_report(all_results)

    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📄 Reporte guardado en: {output_path}")

    # Mostrar resumen en stdout
    print("\n" + report)


if __name__ == "__main__":
    # Constantes para lookups rápidos
    period_14 = 14 + 1  # mínimo de velas para RSI(14)
    max_horizon_steps = 48  # máximo horizon (48h = 2 días para señales de 24h horizon)
