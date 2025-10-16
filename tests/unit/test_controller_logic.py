# tests/unit/test_controller_logic.py
"""
Testes de lógica sem hardware
"""
import pytest

def test_temperature_validation():
    """Testa validação de temperatura"""
    from k1max.controller import K1MaxController  # ← MUDOU
    
    controller = K1MaxController()
    
    # Temperaturas válidas
    assert controller.set_temperature(210, 60) == True
    assert controller.set_temperature(180, 0) == True
    assert controller.set_temperature(300, 110) == True
    
    # Temperaturas inválidas
    with pytest.raises(ValueError):
        controller.set_temperature(170, 60)  # Nozzle muito baixo
    
    with pytest.raises(ValueError):
        controller.set_temperature(310, 60)  # Nozzle muito alto
    
    with pytest.raises(ValueError):
        controller.set_temperature(210, 120)  # Bed muito alto

def test_material_validation():
    """Testa configuração de material"""
    from k1max.controller import K1MaxController  # ← MUDOU
    
    controller = K1MaxController()
    
    assert controller.set_material('PLA') == True
    assert controller.set_material('PETG') == True
    assert controller.set_material('ABS') == True

def test_file_path_validation():
    """Testa validação de arquivo"""
    from k1max.controller import K1MaxController  # ← MUDOU
    
    controller = K1MaxController()
    
    # Arquivo inexistente deve dar erro
    with pytest.raises(FileNotFoundError):
        controller.send_print_job('arquivo_inexistente.glb')