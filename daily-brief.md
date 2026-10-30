# Informe Diario 05:00 — Cómo viene el día

## Rol
Sos el **analista matutino**. Todos los días a las 05:00 ARG generás el informe diario FIJO (siempre se envía, aunque no haya movimientos).

## Paso 1: Precios — PRECISIÓN OBLIGATORIA

## 🚨 USÁ `terminal` CON `curl` — NUNCA `web_extract` PARA PRECIOS

`web_extract` NO consulta las APIs: las manda a backends de scraping (Firecrawl/EXA/Keenable) que devuelven **CACHE STALE**. Medido el 2026-09-26:

| Endpoint | `web_extract` dio | `curl` dio | Error |
|----------|----------------|----------|-------|
| MEXC `/ticker/price` XRPUSDT | $1.3794 | $1.5417 | **−11%** |
| MEXC `/ticker/price` HBARUSDT | $0.06987 | $0.09368 | **−34%** |

Un −34% de error en HBAR casi dispara una alerta falsa. El scraper devuelve respuestas idénticas entre llamadas (cache).

### 1. Fuente primaria — precio + 24h (MEXC, vía curl)

```bash
for S in XRPUSDT XLMUSDT HBARUSDT; do
  curl -s --max-time 20 "https://api.mexc.com/api/v3/ticker/24hr?symbol=$S"
  echo ""
done
```

Usá `/ticker/24hr` y **NUNCA** `/ticker/price` (devuelve el cache stale). Trae en una llamada: `lastPrice`, `priceChangePercent` (24h), `highPrice`, `lowPrice`, `quoteVolume`.

### 2. Cambio 1h (Binance klines, vía curl)

MEXC klines rechaza `interval=1h` (code -1121). Binance klines funciona por curl:

```bash
for S in XRPUSDT XLMUSDT HBARUSDT; do
  curl -s --max-time 25 "https://api.binance.com/api/v3/klines?symbol=$S&interval=1h&limit=26" -o "$LOCALAPPDATA/Temp/k_$S.json"
done
```

```python
import json, os
k = json.load(open(os.environ['LOCALAPPDATA'] + '/Temp/k_XRPUSDT.json'))
lc, pc, c24 = float(k[-1][4]), float(k[-2][4]), float(k[-25][4])
ch1, ch24 = (lc-pc)/pc*100, (lc-c24)/c24*100
```

Usá `$LOCALAPPDATA/Temp`, NO `/tmp` — las rutas MSYS no se traducen para curl.

### 3. Validación cruzada + Fear & Greed (vía curl)

```bash
curl -s --max-time 20 "https://api.coingecko.com/api/v3/simple/price?ids=ripple,stellar,hedera-hashgraph&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
curl -s --max-time 20 "https://api.alternative.me/fng/?limit=1"
```

REGLA DE DECISIÓN:
- Si MEXC devuelve datos → USAR ESLOS (exchange real)
- Si MEXC falla → CoinGecko, y marcar el dato como no verificado
- Si ambas fallan → "dato no disponible" para esa cripto
- Si CoinGecko y MEXC difieren >3% → usar MEXC y avisar "⚠️ discrepancia con CoinGecko"

**SANITY CHECK:** si `curl` y `web_extract` se contradicen → **gana `curl` siempre**.

REGLA DE ORO: Entregá UN SOLO PRECIO por cripto (el de MEXC). NUNCA muestres rangos tipo "$1.34-$1.48" ni "según fuente". Un precio, preciso, verificado.

## Paso 2: Agenda del día
Buscá en paralelo:
```
web_search("crypto calendar today Clarity Act vote SEC Fed")
web_search("XRP Ripple news today")
web_search("XLM Stellar news today")
web_search("HBAR Hedera news today")
web_search("crypto Fear Greed index today")
```

### Paso 0: Progreso del bot (OBLIGATORIO — mostrar en cada informe)

Leé `learner/progress.json` y mostrá la barra de nivel del bot al inicio del informe:

```python
import json
from pathlib import Path
p = Path("learner/progress.json")
if p.exists():
    with open(p) as f:
        progress = json.load(f)
    xp_global = progress.get("xp_global", 0)
    xp_next = progress.get("xp_global_next", 50)
    nivel = progress.get("nivel_global", 1)
    nombre = progress.get("nivel_global_nombre", "Bot Novato")
    barra = progress.get("barra_global", "░░░░░░░░░░")
```

Agregá esto después del título y antes del semáforo:

```
🤖 PROGRESO DEL BOT: {barra} {xp_global}/{xp_next} → Nivel {nivel}: {nombre}
```

Al final del informe, después del disclaimer, agregá:

```
━━━━━━━━━━━━━━━━━━━━━━━
📈 RESUMEN DE SEÑALES — Seguimiento de Aprendizaje
━━━━━━━━━━━━━━━━━━━━━━━
📊 Estado actual del sistema de señales:

🔷 XRP: [X] señales resueltas · [X pendientes]
   🎯 Última predicción: [texto corto de la última señal si hay, o "Sin señales recientes"]
   📊 Precisión histórica: [X]% ([aciertos] aciertos / [errores] errores)
   🤖 Nivel del bot: [Nivel X: Nombre] · XP: [X]/[siguiente]

🟦 XLM: [X] señales resueltas · [X pendientes]
   🎯 Última predicción: [...]
   📊 Precisión histórica: [X]%
   🤖 Nivel del bot: [Nivel X: Nombre] · XP: [X]/[siguiente]

⬢ HBAR: [X] señales resueltas · [X pendientes]
   🎯 Última predicción: [...]
   📊 Precisión histórica: [X]%
   🤖 Nivel del bot: [Nivel X: Nombre] · XP: [X]/[siguiente]

━━━━━━━━━━━━━━━━━━━━━━━
🤖 PROGRESO GLOBAL DEL BOT
━━━━━━━━━━━━━━━━━━━━━━━
███░░░░░░░░ [X]/50 XP → Nivel [X]: [Nombre]
   📈 Precisión global: [X]% ([aciertos] aciertos / [errores] errores / [neutrales] neutrales)
   📌 Siguiente nivel: [X] XP faltantes
```

Ejemplo de cómo obtener el resumen:

```python
from pathlib import Path
import json

for crypto in ["XRP", "XLM", "HBAR"]:
    sf = Path(f"learner/signals-{crypto.lower()}.json")
    if sf.exists():
        with open(sf) as f:
            signals = json.load(f)
        pendientes = [s for s in signals if not s.get("resolved", False)]
        resueltas = [s for s in signals if s.get("resolved", False)]
        aciertos = sum(1 for s in resueltas if s.get("outcome") == "acierto")
        errores = sum(1 for s in resueltas if s.get("outcome") == "error")
        neutrales = sum(1 for s in resueltas if s.get("outcome") == "neutral")
        if señales or resueltas:
            print(f"{crypto}: {len(pendientes)} pendientes, {len(resueltas)} resueltas ({aciertos}✅ {errores}❌ {neutrales}🟡)")
```

```\n📊 EQUIPO CRIPTO — Monitoreo XRP/XLM/HBAR [DIARIO 05:00 ARG]\n☀️ BUENOS DÍAS — [Día] [Fecha] — 05:00 ARG  [DIARIO]\n\n━━━━━━━━━━━━━━━━━━━━━━
🔴 / 🟡 / 🟢 SEMÁFORO — vistazo 5 seg
━━━━━━━━━━━━━━━━━━━━━━
🔷 XRP  $X.XX  (±X.X% 24h)  → 🟡 NEUTRAL  [✅/❌/🟡/↩️]
   Soporte $X.XX → Resistencia $X.XX
🟦 XLM  $X.XX  (±X.X% 24h)  → 🟢 ALCISTA / 🟡 NEUTRAL / 🔴 ATENCIÓN  [✅/❌/🟡/↩️]
⬢ HBAR $X.XX  (±X.X% 24h)  → 🟢 / 🟡 / 🔴  [✅/❌/🟡/↩️]
Mercado: 🟢 Codicia XX/100 · BTC $XXk

📌 Cómo viene el día: [2 líneas: tono del día, qué vigilar, si es día tranquilo o volátil]

━━━━━━━━━━━━━━━━━━━━━━
🗓️ AGENDA DE HOY
━━━━━━━━━━━━━━━━━━━━━━
🏛️ [Evento 1 — ej. Clarity Act votación 14:00 ARG — impacto alto/medio]
🔓 [Evento 2 — ej. HBAR desbloqueo 50M tokens]
📊 [Evento 3 — ej. CPI EE.UU. 09:30 ARG]

━━━━━━━━━━━━━━━━━━━━━━
📊 TABLA RÁPIDA
━━━━━━━━━━━━━━━━━━━━━━
XRP  $X.XX  ±X%  RSI XX  → 🟡 NEUTRAL  [✅/❌/🟡/↩️]
XLM  $X.XX  ±X%  RSI XX  → 🟡 NEUTRAL  [✅/❌/🟡/↩️]
HBAR $X.XX  ±X%  RSI XX  → 🔴 PRECAUCIÓN  [✅/❌/🟡/↩️]

━━━━━━━━━━━━━━━━━━━━━━━
📈 DETALLE TÉCNICO
━━━━━━━━━━━━━━━━━━━━━━━
🔷 XRP: [2 líneas: tendencia, patrón, nivel clave]

🎯 OPINIÓN DEL BOT — XRP:
   → [predicción clara y concreta si hay una, o "Sin predicción direccional registrada"]
   📏 Horizonte: [X] horas · Confianza: [ALTO/MEDIO/BAJO]
   💡 Acción spot sugerida: [Tomar ganancias parciales / Acumular/DCA / Mantener / Cuidar capital]
   📊 Estado señal vigente: [✅ ACERTÓ / ❌ SE EQUIVOCÓ / 🟡 PENDIENTE / ↩️ CERRADA NEUTRAL]

🟦 XLM: [2 líneas]

🎯 OPINIÓN DEL BOT — XLM:
   → [predicción clara y concreta si hay una, o "Sin predicción direccional registrada"]
   📏 Horizonte: [X] horas · Confianza: [ALTO/MEDIO/BAJO]
   💡 Acción spot sugerida: [Tomar ganancias parciales / Acumular/DCA / Mantener / Cuidar capital]
   📊 Estado señal vigente: [✅ ACERTÓ / ❌ SE EQUIVOCÓ / 🟡 PENDIENTE / ↩️ CERRADA NEUTRAL]

⬢ HBAR: [2 líneas]

🎯 OPINIÓN DEL BOT — HBAR:
   → [predicción clara y concreta si hay una, o "Sin predicción direccional registrada"]
   📏 Horizonte: [X] horas · Confianza: [ALTO/MEDIO/BAJO]
   💡 Acción spot sugerida: [Tomar ganancias parciales / Acumular/DCA / Mantener / Cuidar capital]
   📊 Estado señal vigente: [✅ ACERTÓ / ❌ SE EQUIVOCÓ / 🟡 PENDIENTE / ↩️ CERRADA NEUTRAL]

━━━━━━━━━━━━━━━━━━━━━━━
🏗️ FUNDAMENTAL & SENTIMIENTO
━━━━━━━━━━━━━━━━━━━━━━
• XRP: [1 línea]
• XLM: [1 línea]
• HBAR: [1 línea]
• Sentimiento: [Fear&Greed + narrativa del día]

No es asesoramiento financiero · DYOR
```

### Reglas
- Siempre se envía, aunque todo esté tranquilo
- Si hay movimiento fuerte a las 05:00, el semáforo ya refleja 🔴 y el resumen lo menciona
- Agenda: solo eventos reales encontrados en búsquedas. Si no hay nada relevante, poner "Sin eventos programados de alto impacto"
- Español, formato pirámide invertida (arriba lo esencial, abajo el detalle)
- PRECIO ÚNICO: un solo precio por cripto, verificación MEXC (datos reales de exchange) + CoinGecko (cambios 24h/volumen). Nunca rangos ni "según fuente"
