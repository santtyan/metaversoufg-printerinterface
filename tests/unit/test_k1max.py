# tests/unit/test_k1max.py
"""
Testes do K1MaxController
"""
import pytest

def test_controller_initialization():
    """Testa inicialização do controller"""
    from k1max.controller import K1MaxController
    
    controller = K1MaxController()
    assert controller is not None
    assert controller.monitor is not None

def test_monitor_initialization():
    """Testa inicialização do monitor"""
    from k1max.monitor import K1MaxMonitor
    
    monitor = K1MaxMonitor("192.168.20.175")
    assert monitor.ws_uri == "ws://192.168.20.175:9999"