import json, uuid, datetime as dt

now = dt.datetime.now(dt.timezone.utc)
ts = now.strftime('%Y-%m-%dT%H:%M:%SZ')
rid = str(uuid.uuid4())

# ---------- 1. Orchestrator log ----------
sig = json.load(open('orchestrator_signals.json'))
if isinstance(sig, dict):
    sig = [sig]
rec = {
  "run_id": rid, "timestamp": ts,
  "criptos": {
    "XRP":  {"precio": 1.4977,  "cambio_1h_pct": 0.29,  "cambio_24h_pct": 0.27,
             "alerta": False, "near_miss": False, "near_miss_tipo": None, "near_miss_cerca_de": None, "near_miss_distancia": None},
    "XLM":  {"precio": 0.2243,  "cambio_1h_pct": 0.45,  "cambio_24h_pct": -0.58,
             "alerta": False, "near_miss": False, "near_miss_tipo": None, "near_miss_cerca_de": None, "near_miss_distancia": None},
    "HBAR": {"precio": 0.10354, "cambio_1h_pct": 0.70,  "cambio_24h_pct": -14.94,
             "alerta": True,  "near_miss": False, "near_miss_tipo": None, "near_miss_cerca_de": None, "near_miss_distancia": None}
  },
  "alerta_generada": True, "cripto_en_alerta": "HBAR", "tipo_alerta": "24h_grande",
  "movimiento_detalle": "HBAR -14.94% 24h (MEXC) / -15.02% (Binance, cruzados); pico $0.13096 -> minimo $0.09938, capitulacion con volumen 8.5x; base en $0.1024-$0.1054 con volumen 0.14x del promedio",
  "nota": "CoinGecko 403 (CloudFront) este tick - sin validacion cruzada. Klines-24h derivado (-15.08%) coincide con ticker (<0.5pt) -> sin discrepancia. Binance klines ok via curl (CoinGecko y MEXC klines 1h no disponibles)."
}
sig.append(rec)
json.dump(sig, open('orchestrator_signals.json','w'), ensure_ascii=False, indent=1)

# ---------- 2. Learning signal (HBAR) ----------
h = json.load(open('signals-hbar.json'))
sid = str(uuid.uuid4())
signal = {
  "id": sid, "crypto": "HBAR", "timestamp": ts,
  "signal_type": "consolidation_range", "direction": "NEUTRAL",
  "prediction": "HBAR construye base en $0.1015-$0.1080 durante las proximas 6-10h tras la capitulacion de $0.0994; test probable de $0.1080. Invalidador bajista: cierre 1h bajo $0.0994 proyecta $0.0924-$0.0961. Invalidador alcista: cierre 1h sobre $0.1100 con volumen >$3M reabre $0.1150-$0.1215.",
  "price_at_signal": 0.10365, "confidence": "MEDIO",
  "rationale": "RSI(14) 1h=19.0 en sobreventa extrema; 8 cierres 1h consecutivos en $0.10293-$0.10544 (base estrecha) con volumen 0.14x el promedio 24h ($0.51M vs $3.71M) = agotamiento de venta. Fear&Greed global 73 (Greed) mientras HBAR cae 15%: idiosyncratic, no venta de mercado. Sin noticia negativa especifica hallada. MACD sigue bajo cero (-0.0047) sin aceleracion.",
  "market_regime": "alta_volatilidad",
  "horizon_hours": 8,
  "resolve_by": (now + dt.timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%SZ'),
  "resolved": False, "outcome": "pendiente"
}
required = ["id","crypto","timestamp","signal_type","direction","prediction","price_at_signal",
            "confidence","rationale","market_regime","horizon_hours","resolve_by","resolved","outcome"]
missing = [k for k in required if k not in signal or signal[k] is None or (isinstance(signal[k],str) and signal[k].strip()=="")]
if missing:
    print("NO REGISTRADA, faltan:", missing)
else:
    h.append(signal)
    json.dump(h, open('signals-hbar.json','w'), ensure_ascii=False, indent=1)
    print("SIGNAL_ID", sid)
print("RUN_ID", rid, "| orchestrator records:", len(sig), "| hbar signals:", len(h))
