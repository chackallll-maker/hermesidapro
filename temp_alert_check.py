import json
from datetime import datetime, timezone
from pathlib import Path

data = {
    "ripple": {"usd": 1.51, "usd_market_cap": 94711002579.81, "usd_24h_vol": 5089365627.93, "usd_24h_change": -6.77},
    "stellar": {"usd": 0.203397, "usd_market_cap": 7106405230.04, "usd_24h_vol": 346088830.19, "usd_24h_change": -6.96},
    "hedera-hashgraph": {"usd": 0.09125, "usd_market_cap": 3999662617.74, "usd_24h_vol": 158945502.78, "usd_24h_change": -6.91}
}

criptos = {
    "XRP": {"id": "ripple", "data": data["ripple"]},
    "XLM": {"id": "stellar", "data": data["stellar"]},
    "HBAR": {"id": "hedera-hashgraph", "data": data["hedera-hashgraph"]}
}

now_iso = "2026-09-24T04:49:46Z"

registro = {
    "run_id": now_iso,
    "timestamp": now_iso,
    "criptos": {},
    "alerta_generada": False,
    "cripto_en_alerta": None,
    "tipo_alerta": None,
    "movimiento_detalle": "sin movimiento significativo"
}

alertas = []
for nombre, info in criptos.items():
    d = info["data"]
    ch24 = d["usd_24h_change"]
    alerta = False
    near_miss = False
    near_miss_tipo = None
    near_miss_cerca_de = None
    near_miss_distancia = None

    # Near-miss 1h no disponible, omitimos
    # Near-miss 24h
    if -10 <= ch24 < -7:
        near_miss = True
        near_miss_tipo = "24h_cerca_alerta_negativa"
        near_miss_cerca_de = -10.0
        near_miss_distancia = round(abs(ch24 - (-10.0)), 1)
    elif 7 < ch24 <= 10:
        near_miss = True
        near_miss_tipo = "24h_cerca_alerta_positiva"
        near_miss_cerca_de = 10.0
        near_miss_distancia = round(abs(ch24 - 10.0), 1)

    registro["criptos"][nombre] = {
        "precio": d["usd"],
        "cambio_1h_pct": None,
        "cambio_24h_pct": round(ch24, 2),
        "alerta": alerta,
        "near_miss": near_miss,
        "near_miss_tipo": near_miss_tipo,
        "near_miss_cerca_de": near_miss_cerca_de,
        "near_miss_distancia": near_miss_distancia
    }

registro["alerta_generada"] = len(alertas) > 0
registro["cripto_en_alerta"] = alertas[0][0] if alertas else None
registro["tipo_alerta"] = alertas[0][2] if alertas else None

p = Path("C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/learner/orchestrator_signals.json")
existing = json.loads(p.read_text())
if "$schema" in existing or "descripcion" in existing:
    new_list = [registro]
else:
    new_list = existing + [registro]

p.write_text(json.dumps(new_list, indent=2, ensure_ascii=False))

print("✅ Registro escrito")
print(json.dumps(registro, indent=2))
