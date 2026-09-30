# Sistema de Aprendizaje — Registro de Señales y Outcomes

## Propósito

Cada vez que el orquestador o un analista emite una señal predictiva (no solo un dato, sino una *interpretación* con dirección de mercado), se registra en el historial. Pasado el horizonte de tiempo, se mide el resultado real y se actualiza el perfil del especialista.

Con el tiempo, el sistema descubre:
- Qué tipos de señales funciona bien para cada cripto
- Qué tan confiable es cada nivel de confianza declarado
- Bajo qué regímenes de mercado las señales fallan o aciertan
- Patrones crytoespecíficos que ningún analista genérico captaría

---

## Señales que Registramos

Toda señal registra:

| Campo | Descripción |
|-------|-------------|
| `id` | UUID único de la señal |
| `crypto` | XRP / XLM / HBAR |
| `timestamp` | Cuándo se emitió (ISO 8601, UTC) |
| `signal_type` | Categoría de la señal (ver taxonomía abajo) |
| `direction` | ALCISTA / BAJISTA / NEUTRO |
| `prediction` | Qué se predijo (texto libre, pero concreto) |
| `price_at_signal` | Precio del activo cuando se emitió |
| `confidence` | ALTO / MEDIO / BAJO — cuán seguro estaba el bot |
| `rationale` | Por qué se emitió (indicadores, noticia, patrón) |
| `horizon_hours` | Cuánto tiempo esperamos para medir el resultado |
| `resolve_by` | Timestamp (UTC) cuando debe medirse el outcome |
| `resolved` | `false` todavía |
| `outcome` | Llenado al resolver: `acierto` / `error` / `neutral` / `pendiente` |
| `outcome_detail` | Qué pasó realmente (precio final, % move, etc.) |
| `accuracy_note` | Si acertó pero por casualidad, o error pero por algo inesperado |

---

## Taxonomía de Señales

### Técnicas

- `rsi_overbought_reversal` — RSI>70, se predice corrección
- `rsi_oversold_rebound` — RSI<30, se predice rebote
- `macd_bullish_cross` — MACD cruza señal hacia arriba
- `macd_bearish_cross` — MACD cruza señal hacia abajo
- `support_breakdown` — Precio rompe soporte con volumen
- `resistance_breakout` — Precio rompe resistencia con volumen
- `trend_continuation` — Tendencia establecida, se predice continuidad
- `trend_reversal_pattern` — Patrón de reversión detectado (doji, martillo, envolvente, etc.)
- `volume_confirmation` — Volumen confirma dirección del movimiento
- `volume_divergence` — Volumen diverge de precio (señal de debilidad)
- `support_retest` — Precio retestea el soporte, se predice rebote
- `support_hold_continuation` — Soporte se sostiene, se predice continuación
- `consolidation_range` — Se predice rango lateral (se evalúa por banda, no por dirección)
- `resistance_rejection` — Rechazo en resistencia, se predice baja
- `breakout_confirmation` — Confirmación de ruptura por encima de la referencia
- `momentum_decay` — Pérdida de momentum, se predice baja >=1%

### Fundamentales / Catalizadores

- `news_positive_impact` — Noticia positiva, se predice suba
- `news_negative_impact` — Noticia negativa, se predice baja
- `event_catalyst` — Evento programado (desbloqueo, votación, launch) con predicción de impacto
- `regime_change` — Cambio de régimen detectado (ej. de lateral a tendencia)

### De Sentimiento

- `sentiment_shift` — Cambio detectable en sentimiento (ej. Twitter positivo + Reddit negativo = divergencia)
- `fear_greed_extreme` — Fear & Greed en extremo, se predice reversión
- `whale_accumulation` — Detección de acumulación de whales

---

## ⚠️ Tipos de señal sin criterio de outcome

Todo `signal_type` nuevo debe tener entrada en `ACCION_CRITERIA` de
`resolve_signals.py`. Si no la tiene, el resolver devuelve `neutral` con
`"Tipo de señal desconocido"` y **contamina la estadística de acierto** en
silencio. Desde 2026-09-27 el resolver imprime un warning explícito a stderr
cuando esto ocurre.

---

## Medición de Outcome

### Configuración por tipo de señal

| Signal type | Horizon típico | Criterio de acierto |
|-------------|---------------|---------------------|
| rsi_overbought_reversal | 4-8h | Precio baja ≥2% desde precio de señal |
| rsi_oversold_rebound | 4-8h | Precio sube ≥2% desde precio de señal |
| macd_bullish_cross | 24h | Precio es mayor al precio de señal al cierre del horizonte |
| macd_bearish_cross | 24h | Precio es menor al precio de señal al cierre del horizonte |
| support_breakdown | 12h | Precio está por debajo del soporte al cierre del horizonte |
| resistance_breakout | 12h | Precio está por encima de la resistencia al cierre del horizonte |
| news_positive_impact | 6h | Precio sube ≥1.5% desde precio de señal |
| news_negative_impact | 6h | Precio baja ≥1.5% desde precio de señal |
| sentiment_shift | 12h | Dirección del precio coincide con la dirección del cambio de sentimiento |
| fear_greed_extreme | 24h | Reversión ≥3% en dirección opuesta al extremo |
| whale_accumulation | 48h | Precio sube o se mantiene estable (no baja significativamente) |

### Estado del outcome

- `acierto` — La predicción se cumplió dentro del horizonte
- `error` — La predicción no se cumplió
- `neutral` — El precio no se movió significativamente (ruido)
- `pendiente` — Aún no llegó el horizonte de resolución
- `anulada` — La señal fue anulada antes del horizonte (ej. condiciones cambiaron drásticamente)

### Resolución automática (HECHA — pipeline activo)

El job de cron **"Sistema de Aprendizaje — Resolución automática de señales"** (`6e241c20b73b`) ejecuta `resolve_signals.py` cada 360min (6h). Este script:
1. Escanea `signals-<crypto>.json` para cada cripto
2. Encuentra señales con `resolved=false` y `resolve_by < ahora()`
3. Obtiene el precio actual desde CoinGecko API
4. Calcula el outcome usando los criterios por tipo de señal
5. Actualiza el JSON con `resolved=true`, `outcome`, `outcome_detail`, `accuracy_note`
6. Ejecuta `analyze.py --update-profiles` para recalcuiar estadísticas
7. Ejecuta `xp_tracker.py --update` para recalcular niveles y XP

**Nota:** Este job está fallando actualmente porque apunta a un modelo OpenRouter que no existe. Ver `health-check.md` para diagnosticar.

Cualquiera puede ejecutar la resolución manualmente en cualquier momento:

```bash
cd "C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor"
python resolve_signals.py
python learner/analyze.py --update-profiles
python learner/xp_tracker.py --update
```

---

## Actualización del Especialista

Cuando se resuelve una señal, el archivo `specialist-<crypto>.md` se actualiza con:

1. **Stat precisión por tipo de señal**: ej. `rsi_overbought_reversal: 62% (18/29)`
2. **Stat precisión por nivel de confianza**: ej. `ALTO: 71%, MEDIO: 54%, BAJO: 38%`
3. **Nota de régimen**: si la señal ocurrió en un régimen específico (noticias, alta volatilidad, lateral), se anota
4. **Patrones crytoespecíficos**: observaciones cualitativas que surgen de los datos

---

## Archivos del Sistema

```
learner/
├── registry.md              — Qué señales registramos y cómo medimos resultados
├── signal-schema.json       — Formato estructurado de cada señal
├── signals-xrp.json         — Historial de señales de XRP (se va llenando)
├── signals-xlm.json         — Historial de señales de XLM
├── signals-hbar.json        — Historial de señales de HBAR
├── specialist-xrp.md        — Perfil de especialista XRP (se actualiza con los datos)
├── specialist-xlm.md        — Perfil de especialista XLM
├── specialist-hbar.md       — Perfil de especialista HBAR
├── progress.json            — Estado actual de niveles, XP y barra de progreso
├── analyze.py               — Script que analiza historial y produce estadísticas
├── xp_tracker.py            — Tracker de niveles y XP del bot (gamificación)
├── register_from_alert.py   — Registra señales desde archivos de alerta existentes
└── backtest.py              — Backtester: mide precisión histórica de señales en datos reales
```

Scripts de nivel proyecto (fuera de learner/):
```
├── resolve_signals.py       — Resuelve señales pendientes desde CoinGecko + actualiza perfiles
├── update_specialist.py     — Actualiza perfiles specialist-*.md con estadísticas
├── markets_check.py         — Diagnóstico rápido de mercados
```

---

## Flujo de Trabajo

1. **Emitir señal** → El analista/orquestador registra la señal en `signals-<crypto>.json`
2. **Esperar horizonte** → La señal queda pendiente
3. **Resolver** → Se consulta precio actual, se llena `outcome`
4. **Analizar** → `analyze.py` procesa el historial y actualiza el perfil del especialista
5. **Iterar** → La próxima señal usa el perfil actualizado para calibrar confianza

---

## Integración con el Orquestador

El orchestrator.md se modifica para:
- Antes de emitir una alerta, consultar el perfil del especialista para esa cripto
- Si la alerta contiene una predicción direccional, registrarla en el JSON correspondiente
- Incluir en el informe de alerta, si es relevante: "Basado en N señales similares, precisión histórica: X%"

```

```
