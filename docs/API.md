# API Reference

## K1MaxController

### `is_printing() -> bool`
Verifica impressão ativa via WebSocket.
```python
if controller.is_printing():
    print("Ocupada")
```

---

### `is_ready() -> bool`
Verifica disponibilidade (idle + fria <50°C).
```python
if controller.is_ready():
    print("Pronta")
```

---

### `set_material(material: str) -> bool`
Valida material (PLA/PETG/ABS/TPU). Aplicado em `send_print_job()`.
```python
controller.set_material('PLA')
```

---

### `set_temperature(nozzle: int, bed: int) -> bool`
Valida temperaturas (nozzle: 180-300°C, bed: 0-110°C). Aplicado em `send_print_job()`.

**Raises:** `ValueError` se fora dos limites.
```python
controller.set_temperature(210, 60)
```

---

### `send_print_job(file_path: str) -> bool`
Envia arquivo aplicando configurações.

**Workflow:** Valida → Converte GLB→STL → Fatia → Envia (GUI automation)

**Raises:** `FileNotFoundError` se arquivo não existe.
```python
controller.set_material('PLA')
controller.set_temperature(210, 60)
controller.send_print_job('models/objeto.glb')
```

---

## MetaversoAPIClient

### `authenticate()`
Autentica e armazena token.

---

### `get_printable_objects() -> List[Dict]`
Lista objetos disponíveis.

---

### `mark_object_printing(object_id: str)`
Marca objeto como imprimindo.

---

### `save_object_file(object_id: str, path: str)`
Baixa arquivo do objeto.
```python
api.save_object_file('abc123', 'models/temp.glb')
```

---

## Workflow Completo
```python
from adapters.metaverso_client import MetaversoAPIClient
from k1max.controller import K1MaxController

api = MetaversoAPIClient()
controller = K1MaxController()

api.authenticate()
objetos = api.get_printable_objects()

if objetos and controller.is_ready():
    obj = objetos[0]
    api.mark_object_printing(obj['object_id'])
    api.save_object_file(obj['object_id'], 'models/temp.glb')
    
    controller.set_material('PLA')
    controller.set_temperature(210, 60)
    controller.send_print_job('models/temp.glb')
```

---

## Limitações Técnicas

- **WebSocket:** Read-only (porta 9999)
- **Comandos escrita:** GUI automation via Creality Print
- **HTTP upload:** Não disponível (testado, erro 500)