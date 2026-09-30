# Especialista XLM — Aprendizaje Acumulado

## Visión General

Este perfil refleja lo que el sistema ha aprendido (o hipotetiza inicialmente) sobre el comportamiento de XLM. Se actualiza cada vez que se resuelven señales pendientes.

---

## Hipótesis Prior (inicial — por confirmar con datos)

### Comportamiento Típico de XLM

XLM (Stellar) es una cripto de **adoption-driven** con enfoque en pagos cross-border y remesas. Su comportamiento tiende a ser:
- Menos noticia-driven que XRP (menos demandas legales, menos drama)
- Más sensible a desarrollos de adopción real (partnerships, casos de uso)
- Mayormente técnico en períodos sin noticias grandes

Correlación con BTC: ~0.75 en régimen normal, puede bajar durante eventos específicos de Stellar.

### Régimen de Mercado

- **Régimen adopción**: cuando hay anuncios de nueva adopción, partnerships significativos, el precio tiende a reaccionar con movimientos sostenidos (no solo esporádicos).
- **Régimen técnico**: la mayoría del tiempo, XLM se comporta más técnicamente, con soportes/resistencias más definidos que XRP.
- **Régimen lateral**: XLM tiende a consolidarse más que XRP en períodos de indecisión del mercado.

### Patrones Crytoespecíficos Observados

1. **RSI en XLM**: tiende a ser más "limpio" que XRP — menos falsos overbought/oversold. Señales de RSI tienen potencialmente mayor predictividad.

2. **Breakouts en XLM**: cuando se confirman con volumen y sostenidos en el tiempo, tienden a llevar a movimientos modestos pero consistentes (no explosivos como XRP pero más sostenidos).

3. **Reacción a noticias de adopción**: XLM responde positivamente a anuncios reales de adopción (no hype). Noticias de partnerships con entidades reales (no solo anuncios de intención) tienen impacto más durable.

4. **Volumen en fines de semana**: similar a XRP, menos volatilidad, señales más confiables.

5. **Sentimiento de comunidad**: la comunidad XLM en Reddit/Twitter tiende a ser menos "boomer" que XRP, más enfocada en tecnología/adoption. Esto puede hacer que el sentimiento social sea un indicador más limpio.

---

## Estadísticas por Tipo de Señal
| Tipo de Señal | Aciertos / Total | Precisión | Notas |
|---------------|------------------|-----------|-------|
| consolidation_range | 0 / 1 | 0% |  |
| continuation_bajista_oversold | 0 / 1 | 0% |  |
| news_negative_impact | 0 / 1 | 0% |  |
| news_positive_impact | 1 / 2 | 50% |  |
| resistance_breakout | 1 / 1 | 100% |  |
| support_retest | 0 / 1 | 0% |  |

## Estadísticas por Nivel de Confianza (inicial — por confirmar)
| Nivel de Confianza | Aciertos / Total | Precisión |
|--------------------|------------------|-----------|
| MEDIO | 2 / 7 | 29% |

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

- Si `rsi_oversold_rebound` tiene >65% precisión, trato XLM como más confiable para señales de rebote que XRP.
- Señales técnicas en XLM: generalmente mantener confianza declarada a menos que haya noticias importantes de Stellar.
- Durante anuncios de adopción real: aumentar confianza en señales de impacto positivo.

---

## Cómo Usar Este Perfil

Cuando el orquestador u otro analista va a emitir una señal para XLM:
1. Buscar el tipo de señal en la tabla de estadísticas
2. Ver precisión histórica y notas
3. Ajustar confianza declaration en consecuencia
4. Verificar si el régimen actual encaja en algún patrón conocido
5. Registrar la señal en `signals-xlm.json` con la confianza calibrativa
