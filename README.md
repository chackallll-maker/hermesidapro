# Sistema de Monitoreo Criptográfico — XRP, XLM, HBAR

## Descripción General

Sistema de monitoreo y análisis automatizado para tres criptomonedas: **XRP (Ripple)**, **XLM (Stellar)** y **HBAR (Hedera)**. Combina un agente orquestador principal con tres especialistas (técnico, fundamental, sentimiento) para producir informes completos de mercado en español.

## Arquitectura

```
┌─────────────────────────────────────────────────┐
│           ORQUESTADOR (orchestrator.md)          │
│   Monitorea precios → Detecta movimientos        │
│   Activa especialistas → Consolida informe      │
└─────────────┬──────────────┬────────────────────┘
              │              │
    ┌─────────▼──┐  ┌───────▼─────┐  ┌──────────────┐
    │  TÉCNICO   │  │ FUNDAMENTAL │  │  SENTIMIENTO │
    │ (RSI,MACD, │  │ (tokenomics,│  │  (noticias,  │
    │  soportes, │  │  adopción,  │  │   redes,     │
    │  volumen)  │  │  equipo)    │  │  fear/greed) │
    └────────────┘  └─────────────┘  └──────────────┘
```

## Archivos del Sistema

| Archivo | Rol |
|---------|-----|
| `README.md` | Este documento — visión general |
| `orchestrator.md` | Agente principal: monitorea precios y activa análisis |
| `technical-analyst.md` | Especialista en análisis técnico |
| `fundamental-analyst.md` | Especialista en análisis fundamental |
| `sentiment-analyst.md` | Especialista en análisis de sentimiento |
| `run-analysis.md` | Ejecutar análisis manual inmediato |

## Criptomonedas Monitoreadas

| Símbolo | Nombre | ID CoinGecko | ID CoinMarketCap |
|---------|--------|--------------|-------------------|
| XRP | Ripple | `ripple` | `52` |
| XLM | Stellar | `stellar` | `512` |
| HBAR | Hedera | `hedera-hashgraph` | `4642` |

## Disparadores de Análisis

El sistema activa análisis automático cuando:
- **Movimiento >5% en 1 hora** → Alerta corta
- **Movimiento >10% en 24 horas** → Alerta extendida

## Fuentes de Datos

- **Precios**: CoinGecko API, CoinMarketCap
- **Noticias**: CoinDesk, Cointelegraph, The Block
- **Redes Sociales**: Twitter/X, Reddit (r/Ripple, r/Stellar, r/hedera)
- **Sentimiento**: Fear & Greed Index, LunarCrush, Santiment
- **On-chain**: Glassnode, Dune Analytics

## Uso Rápido

```bash
# Análisis manual completo (las tres criptos, los tres tipos)
hermes chat -q "Lee y sigue las instrucciones en C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/run-analysis.md"

# Solo monitoreo continuo
hermes chat -q "Lee y sigue las instrucciones en C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/orchestrator.md"

# Análisis técnico de XRP
hermes chat -q "Lee technical-analyst.md y analiza XRP"
```

## Formato de Salida

Cada informe incluye:
1. **Resumen ejecutivo** (2-3 líneas)
2. **Precio actual** y cambio % (1h, 24h, 7d)
3. **Análisis técnico** (RSI, MACD, soportes/resistencias, volumen)
4. **Análisis fundamental** (noticias, adopción, tokenomics)
5. **Sentimiento** (noticias, redes sociales, fear/greed)
6. **Conclusión y nivel de confianza** (ALTO/MEDIO/BAJO)

## Idioma

Todos los informes se generan en **español**.
