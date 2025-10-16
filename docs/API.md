# API Reference

## K1MaxController

### Métodos

#### `is_printing() -> bool`
Verifica se impressão está ativa.

**Retorna:** `True` se imprimindo, `False` se idle.
```python
controller = K1MaxController()
if controller.is_printing():
    print("Impressora ocupada")
```

#### `is_ready() -> bool`
Verifica se pronta para nova impressão.

**Retorna:** `True` se idle e fria (<50°C).

#### `set_material(material: str) -> bool`
Configura material via preset Creality Print.

**Parâmetros:**
- `material` - PLA, PETG, ABS, TPU

#### `set_temperature(nozzle: int, bed: int) -> bool`
Configura temperaturas.

**Parâmetros:**
- `nozzle` - 180-300°C
- `bed` - 0-110°C

#### `send_print_job(file_path: str) -> bool`
Envia arquivo para impressão.

**Parâmetros:**
- `file_path` - Caminho arquivo GLB/STL

**Workflow:**
1. Converte GLB → STL
2. Fatia no Creality Print
3. Envia para impressora