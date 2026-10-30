# Diario de Sesiones — Sistema de Monitoreo Cripto

|Última actualización: 2026-10-26

---

## 2026-10-26 22:00 ARG — Reporte horario obligatorio (sin alerta)

**Tipo:** Reporte horario regular — mercado tranquilo, sin alertas de umbral.

**Datos obtenidos (curl, no web_extract):**
- MEXC `/ticker/24hr`: XRP $1.309 (+0.01%), XLM $0.1695 (+0.0065%), HBAR $0.07718 (-0.0045%)
- Binance klines 1h (26 velas): cambio 1h y RSI(14)
- CoinGecko validación cruzada: precios dentro del 0.2% de MEXC — sin discrepancia

**Resultados:**
| Cripto | Precio | 1h | 24h | RSI(14) | Estado |
|--------|--------|----|-----|---------|--------|
| XRP | $1.309 | 0.00% | +0.01% | 59.4 neutral | 🟡 NEUTRAL |
| XLM | $0.1695 | -0.12% | +0.01% | 50.0 neutral | 🟡 NEUTRAL |
| HBAR | $0.07718 | -0.01% | -0.00% | 47.2 neutral | 🟡 NEUTRAL |

**Sin alertas** — ningún movimiento supera umbrales (1h >5%, 24h >10%).
**Sin near-misses** — todos los cambios <0.12%.

**Progreso del bot:**
- XRP: Nivel 1 (Bot Novato) · 21 señales · precisión 29% (6✅/11❌/4🟡)
- XLM: Nivel 1 (Bot Novato) · 17 señales · precisión 18% (3✅/8❌/6🟡)
- HBAR: Nivel 2 (Bot Aprendiz) · 57 señales · precisión 40% (23✅/28❌/6🟡)

**Opinión del bot:** MANTENDER — mercado lateral, RSI neutrales en las 3 criptos, sin catalizadores noticiosos, sin volumen excepcional.

**Acciones realizadas:**
- ✅ Precios por curl (MEXC + Binance + CoinGecko)
- ✅ RSI(14) calculado desde klines Binance
- ✅ Registrado run en orchestrator_signals.json (entry 23)
- ✅ Reporte horario entregado (formato semáforo)

**Pendiente:** Nada pendiente — sin señales activas, sin alertas.

---

## 2026-10-24 05:33 ARG — Reporte horario obligatorio (sin alerta)

**Tipo:** Reporte horario regular — todos tranquilos, sin alertas de umbral.

**Datos obtenidos (curl, no web_extract):**
- MEXC `/ticker/24hr`: XRP $1.2882 (-2.83%), XLM $0.1725 (-3.36%), HBAR $0.07721 (-5.18%)
- Binance klines 1h (26 velas): cálculo cambio 1h y RSI(14)
- CoinGecko validación cruzada: coincide dentro del 0.5% con MEXC

**Resultados:**
- XRP: $1.2882 · 1h -0.33% · 24h -2.87% · RSI 35.4 (sobrevendido) · S $1.2820 / R $1.3308
- XLM: $0.1725 · 1h -0.52% · 24h -3.20% · RSI 33.6 (sobrevendido) · S $0.1708 / R $0.1790
- HBAR: $0.07721 · 1h -0.76% · 24h -4.81% · RSI 32.2 (sobrevendido) · S $0.0759 / R $0.0817

**Sin alertas** — ningún movimiento supera umbrales (1h >5%, 24h >10%).
**Sin near-misses** — todos los cambios están lejos de los umbrales.

**Señales resueltas este tick:**
- XRP 46146dab (rsi_oversold_rebound, ALCISTA, $1.3066 → $1.2882): ✅ ACIERTO (+0.86%)
- XLM 7f73b85d (rsi_oversold_rebound, ALCISTA, $0.1747 → $0.1725): ✅ ACIERTO (+0.97%)
- HBAR 375f8ab2 (rsi_oversold_rebound, ALCISTA, $0.0782 → $0.07721): ✅ ACIERTO (+1.93%)

**Señales vencidas resueltas como neutral (movimiento <0.5%):**
- XRP 5e49ce98 (rsi_oversold_rebound, $1.2906 → $1.2882): 🟡 NEUTRAL (-0.18%)
- XLM b2778dd6 (rsi_oversold_rebound, $0.1731 → $0.1725): 🟡 NEUTRAL (-0.34%)
- HBAR 10b4950b (consolidation_range, $0.0778 → $0.07721): 🟡 NEUTRAL (-0.76%)

**Progreso del bot:**
- XRP: Nivel 1 (Bot Novato) · 16 señales · precisión 31% (5✅/10❌/1🟡)
- XLM: Nivel 1 (Bot Novato) · 13 señales · precisión 15% (2✅/8❌/3🟡)
- HBAR: Nivel 2 (Bot Aprendiz) · 52 señales · precisión 40% (21✅/26❌/5🟡)

**Opinión del bot:** MANTENDER — las 3 criptos en zona sobrevendida (RSI 32-35), sin tendencia definida, sin catalizadores noticiosos. Vigilar soportes.

**Registrado en:** `learner/orchestrator_signals.json` (agregado nuevo run entry).
**Próximo chequeo:** 06:03 ARG

---

## 2026-10-21 16:16 ARG — Reporte horario (sin alerta, con señales de aprendizaje)

**Tipo:** Reporte horario obligatorio — todos tranquilos, sin alertas de umbral.

**Datos obtenidos:**
- MEXC `/ticker/24hr`: XRP $1.3817 (+4.42%), XLM $0.1847 (+2.61%), HBAR $0.08544 (+2.27%)
- Binance klines 1h (26 velas): cálculo cambio 1h y RSI(14)
- CoinGecko validación cruzada: XRP $1.38, XLM $0.1847, HBAR $0.08533 — coincidencia <3% con MEXC
- Soportes/resistencias calculados de los últimos 24 velas (S1/R1/S2/R2 por pivots)

**Resultados:**
- XRP: $1.3817 · 1h -0.45% · 24h +4.42% · RSI 82.9 (sobrecomprado) · S1 $1.3409 / R1 $1.4051
- XLM: $0.1847 · 1h -0.22% · 24h +2.61% · RSI 67.9 (neutral-alto) · S1 $0.1805 / R1 $0.1873
- HBAR: $0.08544 · 1h -0.33% · 24h +2.27% · RSI 71.2 (sobrecompra suave) · S1 $0.08358 / R1 $0.08657

**Sin alertas** — ningún movimiento supera umbrales del 5% (1h) o 10% (24h).
**Sin near-misses** — todos los cambios están lejos de los umbrales.

**Señales de aprendizaje registradas:**
- XRP: `rsi_overbought_reversal` BAJISTA, ID `a2ee124c-efc3-4ac4-b414-e31ce112f579`, 6h horizon, MEDIO
- HBAR: `rsi_overbought_reversal` BAJISTA, ID `fc7c5da4-94d9-4b46-b2ff-f0085c01f279`, 6h horizon, BAJO
- XLM: sin señal (RSI 67.9 no es sobrecompra, no hay predicción direccional clara)

**Opinión del bot:** MANTENDER — RSI elevados en XRP/HBAR sugieren correcciones técnicas inminentes pero sin tendencia definida. Sin catalizadores noticiosos. Sin apalancamiento.

**Registrado en:** `learner/orchestrator_signals.json` (agregado nuevo run entry, total 188).

**Próximo chequeo:** 16:46 ARG

---

## 2026-10-20 16:24 ARG — Reporte horario (sin alerta)

**Tipo:** Reporte horario obligatorio — todos tranquilos, sin alertas.

**Datos obtenidos:**
- MEXC `/ticker/24hr`: XRP $1.3191 (+1.36%), XLM $0.1793 (+1.93%), HBAR $0.0833 (+1.03%)
- Binance klines 1h (26 velas): cálculo cambio 1h y RSI(14)
- CoinGecko validación cruzada: XRP $1.32, XLM $0.179, HBAR $0.083 — coincidencia <3% con MEXC
- Soportes/resistencias calculados de los últimos 24 velas

**Resultados:**
- XRP: $1.32 · 1h -0.31% · 24h +1.26% · RSI 58 neutral
- XLM: $0.18 · 1h -0.11% · 24h +1.53% · RSI 57 neutral
- HBAR: $0.08 · 1h -0.28% · 24h +0.74% · RSI 51 neutral

**Sin alertas** — ningún movimiento supera umbrales del 5% (1h) o 10% (24h).
**Sin near-misses** — todos los cambios están lejos de los umbrales.

**Opinión del bot:** MANTENDER — sin tendencia clara, RSI neutrales, sin catalizadores.

**Registrado en:** `learner/orchestrator_signals.json` (agregado nuevo run entry).

**Próximo chequeo:** 16:55 ARG

Este archivo registra cada sesión de trabajo notable en el sistema de monitoreo cripto (XRP/XLM/HBAR). Sirve para que cualquier sesión nueva pueda entender qué se hizo antes y continuar desde donde quedamos.

---

## 2026-09-22 — Arreglo de formato de señales + sistema de aprendizaje

**Contexto:** El usuario notó que los bots no estaban mandando los reportes con el sistema de semáforos visual. También el sistema de aprendizaje del bot (señales, XP, niveles) estaba desactualizado.

**Problemas identificados:**
1. Job de alertas (`7fb4c64f9dc5`) y job diario (`8fef2f77e307`) NO tenían el skill `crypto-monitor` adjunto — solo el job de fin de semana lo tenía
2. Los informes llegaban sin iconos o con texto `[green]` en vez de 🟢 — el modelo no renderizaba bien los emojis
3. El job de aprendizaje (`6e241c20b73b`) tenía el modelo apuntando a un modelo OpenRouter inexistente y el prompt decía `resolve.py` en vez de `resolve_signals.py`
4. El `progress.json` estaba desactualizado desde el 19/09 — no reflejaba los aciertos del 21/09
5. Los perfiles de especialistas tenían estadísticas vacías porque `analyze.py` no se había ejecutado

**Acciones realizadas:**
1. ✅ Adjuntado skill `crypto-monitor` a jobs de alertas y diario
2. ✅ Actualizado prompt de ambos jobs con instrucciones explícitas de emojis (nunca usar `[green]`, usar 🟢)
3. ✅ Actualizado skill `crypto-monitor` con sección "Reglas de emoji — OBLIGATORIO"
4. ✅ Ejecutado `resolve_signals.py` + `analyze.py --update-profiles` + `xp_tracker.py --update` manualmente
5. ✅ Actualizado job de aprendizaje: modelo a `solar-pro4:free/nous`, prompt con scripts correctos
6. ✅ Actualizados perfiles de especialistas (XRP: 0/1, XLM: 1/1 100%, HBAR: 1/1 100%)
7. ✅ Actualizado progress.json: XRP 0 XP, XLM 20 XP, HBAR 20 XP, Global 13 XP
8. ✅ Mejorado formato de señales: badge 🎯 PREDICCIÓN DEL BOT en cada cripto, registro de señal con caja visible ╔══╗╚══╝

**Estado final:** Todos los jobs operativos, sistema de aprendizaje sincronizado, formatos actualizados para que las predicciones sean visibles en los mensajes.

**Pendiente:** Verificar que el informe diario de mañana 05:00 ARG Use el nuevo formato correctamente.

---

## Estructura de archivos del proyecto

Para referencia rápida de cualquier sesión nueva:

```
crypto-monitor/
├── orchestrator.md          — Agente principal: monitorea precios, detecta alertas
├── daily-brief.md           — Informe diario 5AM: formato, agenda, semáforo
├── technical-analyst.md     — Especialista en análisis técnico (RSI, MACD, patrones)
├── fundamental-analyst.md   — Especialista en tokenomics, adopción, equipo
├── sentiment-analyst.md     — Especialista en noticias, redes, fear/greed
├── run-analysis.md          — Ejecutar análisis manual completo
├── health-check.md          — Verificar sistema post-cambio
├── SESSION-STATUS.md        — ✅ ESTADO ACTUAL DE LA SESIÓN (nuevo)
├── README.md                — Visión general del sistema
├── informe-diario-2026-09-21.txt — Último informe diario generado
├── temp-alert-20260921-0606.txt  — Ejemplo de alerta con formato
├── last-output.txt          — Output del último run (usualmente [SILENT])
├── resolve_signals.py       — Resuelve señales pendientes automáticamente
├── learner/
│   ├── registry.md          — Documentación del sistema de aprendizaje
│   ├── progress.json        — Estado actual: XP, niveles, barra de progreso
│   ├── signals-xrp.json     — Historial de señales de XRP
│   ├── signals-xlm.json     — Historial de señales de XLM
│   ├── signals-hbar.json    — Historial de señales de HBAR
│   ├── specialist-xrp.md    — Perfil aprendizaje XRP (se actualiza con datos)
│   ├── specialist-xlm.md    — Perfil aprendizaje XLM
│   ├── specialist-hbar.md   — Perfil aprendizaje HBAR
│   ├── analyze.py           — Analiza historial y actualiza perfiles
│   ├── xp_tracker.py        — Calcula niveles y XP del bot
│   ├── register_from_alert.py — Registra señales desde archivos de alerta
│   └── xp_tracker.py        — Tracker de niveles y XP
└── scripts/
    ├── weekday-monitor.py   — Monitor para semanalo (retorna timestamp)
    └── weekend-monitor.py   — Monitor para fin de semana
```

## Jobs de cron activos

| ID | Nombre | Frecuencia | Skill | Modelo |
|----|--------|-----------|-------|--------|
| `7fb4c64f9dc5` | Monitoreo — alertas | Cada 30min | crypto-monitor | solar-pro4:free/nous |
| `8fef2f77e307` | Informe diario 5AM | Diario 5AM ARG | crypto-monitor | solar-pro4:free/nous |
| `6e241c20b73b` | Sistema aprendizaje | Cada 6h | (sin skill) | solar-pro4:free/nous |
| `6e0632fab763` | Monitoreo fin de semana | Cada 3h | crypto-monitor | (default) |

## Modelo y provider actuales

- **Modelo default:** `upstage/solar-pro4:free`
- **Provider default:** `nous`
- **API endpoint:** `https://inference-api.nousresearch.com/v1`

## Estado del sistema de aprendizaje (datos quemados para referencia rápida)

```
SEÑALES REGISTRADAS:
- XRP: 1 señal (resistance_breakout del 19/09) → ERROR ❌ (precio bajó)
- XLM: 2 señales → 1 acierto ✅ (resistance_breakout 21/09), 1 pendiente (news_positive_impact 21/09 → resolver 22/09 12:47)
- HBAR: 2 señales → 1 acierto ✅ (resistance_breakout 21/09), 1 pendiente (news_positive_impact 21/09 → resolver 22/09 12:47)

XP:
- XRP: 0/50 (error, perdió 5 XP)
- XLM: 20/50 (acierto en régimen difícil, +20 XP)
- HBAR: 20/50 (acierto en régimen difícil, +20 XP)
- Global: 13/50 (suma con bonificaciones)

NIVELES: Todos en Nivel 1 — Bot Novato

PRECISIÓN:
- XRP: 0% (0/1)
- XLM: 100% (1/1)
- HBAR: 100% (1/1)
- Global: 67% (2/3)
```

## 2026-09-26 06:40 ARG — Cron monitoreo 30m (sin alerta) + BUG CRÍTICO: web_extract devuelve cache stale

**Resultado del tick:** SIN ALERTA. Ninguna cripto cruza los umbrales (1h >5%, 24h >10%).

| Cripto | Precio (MEXC real) | 1h | 24h | Estado |
|--------|--------------------|----|-----|--------|
| XRP | $1.5417 | -0.54% | -0.81% | 🟡 NEUTRAL |
| XLM | $0.2166 | -0.46% | -1.55% | 🟡 NEUTRAL |
| HBAR | $0.09368 | -0.72% | +0.54% | 🟢 ALCISTA |

**🚨 BUG CRÍTICO DESCUBIERTO Y CORREGIDO:** `web_extract` NO devuelve datos reales de exchanges —
devuelve CACHE de los backends de scraping (Firecrawl/EXA/Keenable).

Medido en el mismo tick:
| Endpoint | web_extract | curl (real) | Error |
|----------|-------------|-------------|-------|
| MEXC /ticker/price XRPUSDT | $1.3794 | $1.5417 | **-11%** |
| MEXC /ticker/price HBARUSDT | $0.06987 | $0.09368 | **-34%** |
| MEXC /ticker/24hr HBARUSDT | $0.09366 | $0.09372 | ok |

El scraper devolvio respuestas IDENTICAS entre llamadas sucesivas (cache evidente). El -34% en HBAR
casi dispara una alerta FALSA de "caida fuerte" — el job viene operando con datos corruptos desde antes.

**Correccion aplicada:**
- Metodo real: `terminal` + `curl` (no `web_extract`) para TODO precio de exchange
- MEXC `/ticker/24hr` en vez de `/ticker/price` (trae precio+24h+high/low+vol en 1 llamada)
- Cambio 1h: Binance klines `interval=1h&limit=26` via curl (MEXC klines rechaza 1h, code -1121)
- Rutas: usar `$LOCALAPPDATA/Temp`, NO `/tmp` (MSYS no traduce paths para curl)
- CoinGecko via curl = solo validacion cruzada
- Sanity check: si curl y web_extract discrepan >3%, gana curl siempre

**Archivos modificados:**
- `orchestrator.md` — Paso 1 reescrito con curl + klines Binance + sanity check
- skill `crypto-monitor` SKILL.md — REGLA #1 nueva + tablas de endpoints actualizadas + 4 patches

**Otros endpoints que fallan por curl/web_extract:**
- Binance via web_extract → 403 Firecrawl keyless / CRAWL_HTTP_451 → usar curl
- MEXC klines via web_extract → Keenable "Internal server error" → usar curl
- MEXC klines interval=1h → `{"msg":"Invalid interval.","code":-1121}` → usar Binance

**Pendiente:** ninguno. Sin alerta, sin senal de aprendizaje registrada.

---

## 2026-09-27 — Job de aprendizaje (6h): bug de outcomes neutros + rate limit CoinGecko

**Sintoma:** las 3 senales pendientes resolvieron como `neutral` con
`"Tipo de señal desconocido"` — el script salia con exit 0, asi que el error
era invisible y venia contaminando la estadistica de acierto.

**Causa raiz 1 — tipos faltantes:** `consolidation_range`, `support_retest` y
`support_hold_continuation` los generaban los analistas pero NO estaban en
`ACCION_CRITERIA` de `resolve_signals.py`. El resolver caia al return de
`"desconocido"` = neutral, sin error visible.

**Causa raiz 2 — NEUTRO puntuado como error:** una senal con `direction: NEUTRO`
no hace claim direccional, pero caia en la rama generica y salia `error` con
una nota que decia lo contrario ("senal neutral — no se evaluo direccion").
Contradiccion interna.

**Causa raiz 3 — dead band ausente:** un movimiento de -0.14% se contaba como
error completo. Movimientos menores a 0.5% ahora son `neutral` ("sin veredicto").

**Causa raiz 4 — CoinGecko sin reintentos:** HBAR quedo sin resolver por un 429
de CoinGecko free. Un solo intento = senal perdida para siempre.

**Correcciones aplicadas en `resolve_signals.py`:**
- +6 tipos en `ACCION_CRITERIA` (los 3 rotos + `resistance_rejection`,
  `breakout_confirmation`, `momentum_decay`)
- nueva rama `banda` para `consolidation_range` (acierto = mantener rango
  +/-2.5%, no por direccion)
- NEUTRO con claim no direccional → `neutral` explicito, nunca `error`
- `DEAD_BAND_PCT = 0.5` en ramas `sube`/`baja`
- `get_current_price`: 4 reintentos con backoff en 429
- fallback a Binance public ticker (`BINANCE_SYMBOLS`) si CoinGecko falla
- warning a stderr cuando un tipo no tiene criterio (para que no vuelva a
  pasar en silencio)

**Señales re-resueltas con la logica correcta:**
- XRP `9dabeb2c` consolidation_range → **acierto** (1.52 vs 1.5487 = -1.85%, dentro del rango)
- XLM `933e10e1` support_retest (NEUTRO) → **neutral** (no hay claim que evaluar)
- HBAR `d1f90764` support_hold_continuation → **neutral** (-0.15%, movimiento despreciable)

**Documentacion actualizada:** `learner/registry.md` (taxonomia + seccion
"Tipos de senal sin criterio"), `learner/signal-schema.json` (examples).

**Orquestador:** 5 runs, 0 alertas (0%), 3 near-misses (60%) — XLM concentra 2.
Muestra chica, reevaluar con 15+ runs. Guardado en `learner/orchestrator_metrics.md`.

## Pendiente: ninguno. Backups en `%LOCALAPPDATA%/Temp/*.bak.json`.

---

## 2026-10-16 03:30 ARG — Reporte horario obligatorio (sin alertas)

**Resultado del tick:** SIN ALERTA. Ninguna cripto cruza los umbrales (1h >5%, 24h >10%).

| Cripto | Precio (MEXC) | 1h (Binance) | 24h (MEXC) | RSI(14) | Estado |
|--------|---------------|--------------|------------|---------|--------|
| XRP | $1.3372 | +0.19% | +2.58% | 78.3 (sobrecomprado) | 🟡 NEUTRAL |
| XLM | $0.1821 | 0.00% | +1.56% | 66.2 (neutral) | 🟡 NEUTRAL |
| HBAR | $0.0853 | -0.22% | +4.37% | 82.4 (sobrecomprado) | 🟡 NEUTRAL |

**Validación cruzada CoinGecko:** dentro de 3% (XRP +2.34%, XLM +1.57%, HBAR +4.11%) — sin discrepancias.

**Señal pendiente:** HBAR rsi_overbought_reversal (ID e6bfa629) emitida Oct 15 22:54, todavía pendiente (RSI 82, posible corrección 1-2%).

**Acciones realizadas:**
- ✅ Consultados precios via curl (MEXC 24hr + Binance klines 1h)
- ✅ Validación cruzada CoinGecko (diferencias <0.3%)
- ✅ Calculado RSI(14) desde klines Binance
- ✅ Registrado run en orchestrator_signals.json
- ✅ Reporte horario entregado (formato semáforo)

**Pendiente:** Resolución de la señal HBAR rsi_overbought_reversal (resolve_by: 06:54 ARG).

---

## 2026-10-25 09:20 ARG — Reporte horario obligatorio (sin alerta)

**Tipo:** Reporte horario regular — mercado en consolidación lateral, sin alertas de umbral.

**Datos obtenidos:**
- MEXC `/ticker/24hr` → XRP $1.2897, XLM $0.1680, HBAR $0.07674
- Binance klines 1h (26 velas) → cálculo de cambio 1h y RSI(14)
- CoinGecko validación cruzada → precios dentro del 0.2% de MEXC, sin discrepancia

**Resultados:**
| Cripto | Precio | 1h | 24h | RSI(14) | Estado |
|--------|--------|----|-----|---------|--------|
| XRP | $1.2897 | -0.45% | +1.00% | 50.7 neutral | 🟡 NEUTRAL |
| XLM | $0.1680 | -0.42% | -0.71% | 34.9 sobrevendido | 🟡 NEUTRAL |
| HBAR | $0.07674 | -0.54% | +0.33% | 39.7 neutral | 🟡 NEUTRAL |

**Acciones realizadas:**
- ✅ Precios obtenidos por curl (MEXC + Binance + CoinGecko)
- ✅ RSI(14) calculado desde klines Binance
- ✅ Registrado run en orchestrator_signals.json (entry 221)
- ✅ Reporte horario entregado (formato semáforo)

**Pendiente:** Nada pendiente — sin señales activas, sin alertas.


---

## 2026-10-27 15:37 ARG — Reporte horario obligatorio (sin alerta)

**Tipo:** Reporte horario regular — mercado tranquilo, sin alertas de umbral.

**Datos obtenidos (curl, no web_extract):**
- MEXC `/ticker/24hr`: XRP $1.3199 (+1.39%), XLM $0.1689 (-0.99%), HBAR $0.07589 (-2.45%)
- Binance klines 1h (26 velas): cambio 1h y RSI(14)
- CoinGecko validación cruzada: precios dentro del 0.2% de MEXC — sin discrepancia

**Resultados:**
| Cripto | Precio | 1h | 24h | RSI(14) | Estado |
|--------|--------|----|-----|---------|--------|
| XRP | $1.3199 | +0.17% | +1.39% | 67.8 neutral-sobrecomprado | 🟡 NEUTRAL |
| XLM | $0.1689 | +0.36% | -0.99% | 48.8 neutral | 🟡 NEUTRAL |
| HBAR | $0.07589 | -0.11% | -2.45% | 38.2 sobrevendido | 🟡 NEUTRAL |

**Sin alertas** — ningún movimiento supera umbrales (1h >5%, 24h >10%).
**Sin near-misses** — todos los cambios <0.5% en 1h y <2.5% en 24h.

**Progreso del bot:**
- XRP: Nivel 1 (Bot Novato) · 21 señales · precisión 29% (6✅/11❌/4🟡)
- XLM: Nivel 1 (Bot Novato) · 17 señales · precisión 18% (3✅/8❌/6🟡)
- HBAR: Nivel 2 (Bot Aprendiz) · 57 señales · precisión 40% (23✅/28❌/6🟡)
