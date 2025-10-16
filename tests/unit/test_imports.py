# tests/unit/test_imports.py
"""Testa imports dos módulos"""

def test_import_controller():
    """Testa import K1MaxController"""
    from k1max.controller import K1MaxController
    assert K1MaxController is not None

def test_import_monitor():
    """Testa import K1MaxMonitor"""
    from k1max.monitor import K1MaxMonitor
    assert K1MaxMonitor is not None

def test_controller_has_5_methods():
    """Verifica 5 métodos obrigatórios"""
    from k1max.controller import K1MaxController
    
    controller = K1MaxController()
    
    assert hasattr(controller, 'is_printing')
    assert hasattr(controller, 'is_ready')
    assert hasattr(controller, 'set_material')
    assert hasattr(controller, 'set_temperature')
    assert hasattr(controller, 'send_print_job')