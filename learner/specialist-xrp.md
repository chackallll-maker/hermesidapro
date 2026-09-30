# Especialista XRP — Aprendizaje Acumulado

## Visión General

Este perfil refleja lo que el sistema ha aprendido (o hipotetiza inicialmente) sobre el comportamiento de XRP. Se actualiza cada vez que se resuelven señales pendientes. Las estadísticas con "insuficiente data" son hipótesis que esperan confirmación con datos reales.

---

## Hipótesis Prior (inicial — por confirmar con datos)

### Comportamiento Típico de XRP

XRP tiende a ser **noticia-driven** más que técnico-puro. Movimientos bruscos suelen estar asociados a:
- Anuncios de Ripple (ODL, partnerships, stablecoin RLUSD)
- Desarrollos legales (victorias, demands, regulaciones)
- Movimientos generales del mercado crypto (correlación con BTC ~0.7-0.8 en régimen normal)

En períodos sin noticias, XRP tiende a comportarse más técnicamente: soportes y resistencias son más relevantes, RSI funciona razonablemente.

### Régimen de Noticias vs Técnico

- **Régimen noticias (Ripple/SEC, partnerships importantes)**: el análisis técnico pierde predictividad. Señales técnicas tienen menor tasa de acierto.
- **Régimen técnico (sin noticias, lateral)**: RSI, MACD, soportes/resistencias son más confiables.

### Patrones Crytoespecíficos Observados

1. **RSI sobrecomprado en XRP**: tiende a corregir más rápido que XLM/HBAR cuando hay noticias negativas, pero puede mantenerse sobrecomprado por más tiempo si hay narrativa bullish fuerte.

2. **Breakouts de resistencia en XRP**: requieren volumen significativo. Breakouts con volumen bajo son frecuentemente falsos.

3. **Movimientos durante announcing hours**: XRP tiende a moverse más durante horario hábil de EE.UU. (13:00-17:00 UTC) si hay noticias relacionadas.

4. **Reacción a Fear & Greed**: XRP reacciona más a sentimiento general del mercado que XLM/HBAR (mayor correlación con BTC).

5. **Volumen en fines de semana**: volatilidad menor, señales técnicas más confiables (menos ruido de noticias).

---

## Estadísticas por Tipo de Señal
| Tipo de Señal | Aciertos / Total | Precisión | Notas |
|---------------|------------------|-----------|-------|
| consolidation_range | 1 / 1 | 100% |  |
| oversold_bounce_ma7 | 1 / 1 | 100% |  |
| resistance_breakout | 0 / 1 | 0% |  |
| rsi_overbought_reversal | 0 / 1 | 0% |  |

## Estadísticas por Nivel de Confianza
| Nivel de Confianza | Aciertos / Total | Precisión |
|--------------------|------------------|-----------|
| MEDIO | 2 / 4 | 50% |

## Régimen de Mercado Actual

Última actualización: 2026-09-29 19:01 UTC

---

## Patrones Confirmados por Datos

*(Se va llenando a medida que las señales se resuelven y el analyze.py identifica patrones estadísticamente significativos)*

---

## Lecciones Aprendidas

*(Observaciones cualitativas que surgen de los datos, no hipótesis)*

---

## Reglas de Calibración para Próximas Señales

*(Basadas en estadísticas reales, no hipótesis)*

- Si `rsi_overbought_reversal` tiene <50% precisión en las últimas 10 señales, reducir confianza en esta señal para XRP.
- Si `support_breakdown` con volumen tiene >70% precisión, aumentar confianza cuando se detecta volumen alto.
- Durante semanas de noticias Ripple/SEC: reducir generalmente la confianza de señales técnicas en 1 nivel (ALTO→MEDIO, MEDIO→BAJO).

---

## Cómo Usar Este Perfil

Cuando el orquestador u otro analista va a emitir una señal para XRP:
1. Buscar el tipo de señal en la tabla de estadísticas
2. Ver precisión histórica y notas
3. Ajustar confianza declaration en consecuencia
4. Verificar si el régimen actual encaja en algún patrón conocido
5. Registrar la señal en `signals-xrp.json` con la confianza calibrativa
