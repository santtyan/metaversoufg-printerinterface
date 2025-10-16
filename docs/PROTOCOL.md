# Protocolo WebSocket K1 Max

## Conexão
```python
ws://192.168.20.175:9999
ping_interval=None  # CRÍTICO: K1 Max não responde PING frames
```

## Tipos de Mensagem

### Broadcast Completo (~1x / 5-10s)
```json
{
  "state": 0,                    // 0=idle, 1=printing
  "printProgress": 0,            // 0-100
  "layer": 0,
  "TotalLayer": 0,
  "nozzleTemp": "25.0",
  "targetNozzleTemp": 0,
  "bedTemp0": "24.0",
  "targetBedTemp0": 0,
  "printFileName": "/path/to/file.gcode",
  "printJobTime": 0,
  "printLeftTime": 0
}
```

### Update Incremental (~10x / segundo)
```json
{
  "nozzleTemp": "190.24"
}
```

## Campos Críticos

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `state` | int | 0=idle, 1=printing |
| `printProgress` | int | 0-100% |
| `nozzleTemp` | string | Temperatura bico (°C) |
| `bedTemp0` | string | Temperatura mesa (°C) |
| `printFileName` | string | Arquivo atual (com material: _PLA_) |

## Limitações

❌ **Comandos de escrita não descobertos**
- Testado G-code via WS → sem resposta
- Testado comandos Klipper → sem resposta
- HTTP upload → erro 500

✅ **Solução:** GUI Automation para comandos