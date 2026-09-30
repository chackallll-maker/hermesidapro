# Health Check — Verificación de Sistema de Monitoreo Cripto

## Propósito
Verificar que el sistema de monitoreo (XRP/XLM/HBAR) esté sano **después de un cambio** o **cuando hay dudas** sobre su estado.

## Cómo ejecutar
```bash
hermes chat -q "Lee y sigue EXACTAMENTE las instrucciones en C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/health-check.md"
```

## Instrucciones para el agente que ejecuta el check

### Paso 1: Verificar cron jobs
Ejecutá `cronjob_manage` con `action='list'` y revisá:

| Check | Esperado | Si falla |
|-------|----------|----------|
| `Monitoreo XRP/XLM/HBAR — alertas` existe y está habilitado | `enabled: true`, `state: scheduled` | ❌ Reportar |
| `Informe diario cripto — 5AM` existe y está habilitado | `enabled: true`, `state: scheduled` | ❌ Reportar |
| `gateway_running` es true | `true` | ❌ Reportar |

Para cada job, verificá:
- `last_status` = `ok` → ✅ sana
- `last_status` = `error` → ⚠️ reportar last_error
- `last_delivery_error` ≠ null → ⚠️ reportar cuál fue el error de entrega
- `next_run_at` está en el futuro → ✅ sana
- `last_run_at` está en el pasado (no es vacío ni futuro) → ✅ sana

### Paso 2: Verificar archivos del proyecto
Revisá que existan y sean legibles:
```
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/README.md
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/orchestrator.md
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/technical-analyst.md
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/fundamental-analyst.md
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/sentiment-analyst.md
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/run-analysis.md
C:/Users/pablo/AppData/Local/hermes/projects/crypto-monitor/daily-brief.md
```

Para cada archivo:
- Existe y es legible → ✅
- No existe / no legible → ❌ reportar

### Paso 3: Reporte final
**Si todo está OK:**
```
✅ SISTEMA SANO — Monitoreo XRP/XLM/HBAR
• 2 jobs activos y programados (próximo: HH:MM)
• Gateway: corriendo
• 7/7 archivos OK
• Último run del monitor: OK (HH:MM)
• Último run del daily: OK (HH:MM)
```

**Si algo falla:**
```
⚠️ SISTEMA CON PROBLEMAS
• [detalle del problema 1]
• [detalle del problema 2]
→ Acción recomendada: [qué hacer]
```

### Reglas
- No asumas, verificá con datos reales.
- Si `cronjob_manage list` falla, avisá que no se pudo verificar la lista de jobs.
- Si un archivo no existe pero el job sigue funcionando, reportalo pero no asumas que está roto.
- Respuesta breve y directa — no narratives.
