# Especialista HBAR — Aprendizaje Acumulado

## Visión General

Este perfil refleja lo que el sistema ha aprendido (o hipotetiza inicialmente) sobre el comportamiento de HBAR. Se actualiza cada vez que se resuelven señales pendientes.

---

## Hipótesis Prior (inicial — por confirmar con datos)

### Comportamiento Típico de HBAR

HBAR (Hedera) es una cripto **enterprise-focused** con gobernanza por council (empresas como Google, IBM, Boeing, LG, etc.). Su comportamiento tiende a ser:
- Menos volátil que XRP/XLM en general
- Más sensible a desenvolvimiento de la governance y anuncios de miembros del council
- Tiene desbloqueos programados de tokens que pueden crear presión de venta periódica
- Menos correlacionado con el mercado general que XRP (correlación con BTC ~0.6-0.7)

### Régimen de Mercado

- **Régimen enterprise**: cuando hay anuncios de adoption enterprise, nuevos miembros del council, casos de uso reales (supply chain, identity, etc.), HBAR puede mover con más sostenibilidad.
- **Régimen técnico**: la mayoría del tiempo, HBAR se comporta de forma más técnica, con rangos más definidos.
- **Régimen de desbloqueos**: cerca de fechas de desbloqueo de tokens, puede haber presión bajista anticipada.

### Patrones Crytoespecíficos Observados

1. **RSI en HBAR**: tiende a ser más suave que XRP/XLM — menos extremos. Overbought/oversold puede durar más porque la volatilidad es menor.

2. **Breakouts en HBAR**: menos frecuentes pero cuando happen, suelen ser más sostenidos porque el volumen de HBAR es menor y los movimientos son más "ponderados".

3. **Desbloqueos de tokens**: eventos programados que pueden crear caídas matemáticas si no hay demanda suficiente para absorber el supply adicional. Hay que monitorear el calendar de desbloqueos.

4. **News de council**: anuncios de nuevos miembros del governing council (empresas Fortune 500, etc.) tienen impacto positivo duradero, no solo esporádico.

5. **Reacción a Fear & Greed**: HBAR es menos reactivo a sentimiento general del mercado que XRP — más independiente.

6. **Staking**: HBAR tiene staking con rewards, lo que puede crear una base de holders más patient y menos propensos a ventas panic.

---

## Estadísticas por Tipo de Señal
| Tipo de Señal | Aciertos / Total | Precisión | Notas |
|---------------|------------------|-----------|-------|
| breakout_confirmation | 0 / 1 | 0% |  |
| consolidation_range | 0 / 12 | 0% |  |
| macd_bearish_cross | 3 / 3 | 100% |  |
| momentum_decay | 1 / 1 | 100% |  |
| resistance_breakout | 1 / 3 | 33% |  |
| rsi_overbought_reversal | 13 / 18 | 72% |  |
| rsi_oversold_rebound | 2 / 15 | 13% |  |
| support_breakdown | 2 / 3 | 67% |  |
| support_hold_continuation | 1 / 2 | 50% |  |

## Estadísticas por Nivel de Confianza (inicial — por confirmar)
| Nivel de Confianza | Aciertos / Total | Precisión |
|--------------------|------------------|-----------|
| ALTO | 1 / 1 | 100% |
| BAJO | 3 / 13 | 23% |
| MEDIO | 19 / 44 | 43% |

## Régimen de Mercado Actual

Última actualización: 2026-10-30 19:27 UTC

---

## Patrones Confirmados por Datos

*(Se va llenando a medida que las señales se resuelven y el analyze.py identifica patrones estadísticamente significativos)*

---

## Lecciones Aprendidas

*(Observaciones cualitativas que surgen de los datos, no hipótesis)*

---

## Reglas de Calibración para Próximas Señales

*(Basadas en estadísticas reales, no hipótesis)*

- Si `rsi_overbought_reversal` tiene <50% precisión, la señal de overbought en HBAR debe tener confianza baja o médiUnless hay confirmación voluminica.
- Preocuparse por desbloqueos próximos: si hay desbloqueo programado en las próximas 48h, reducir confianza en señales alcistas a menos que haya noticia positiva que compense.
- Señales técnicas en HBAR: generalmente más confiables que en XRP durante períodos sin noticias, porque menos ruido de noticias.

---

## Cómo Usar Este Perfil

Cuando el orquestador u otro analista va a emitir una señal para HBAR:
1. Buscar el tipo de señal en la tabla de estadísticas
2. Ver precisión histórica y notas
3. Ajustar confianza declaration en consecuencia
4. Verificar si el régimen actual encaja en algún patrón conocido
5. Registrar la señal en `signals-hbar.json` con la confianza calibrativa
