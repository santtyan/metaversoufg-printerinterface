#!/usr/bin/env python3
"""
Debug: Visualiza resposta REAL do endpoint de autenticação
"""

import requests
import json

def debug_authentication():
    """Mostra exatamente o que o servidor retorna"""
    
    url = "https://metaverso.medialab.ufg.br/v1/auth/login"
    payload = {
        "email": "scanner@example.com",
        "password": "scanner"
    }
    
    print("="*70)
    print("DEBUG: ENDPOINT DE AUTENTICAÇÃO")
    print("="*70)
    print(f"\n[REQUISIÇÃO]")
    print(f"URL: {url}")
    print(f"Método: POST")
    print(f"Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\n[RESPOSTA]")
        print(f"Status Code: {response.status_code}")
        print(f"Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n[BODY RAW]")
        print(response.text)
        
        print(f"\n[BODY PARSED]")
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            print(f"\n[ANÁLISE DAS CHAVES]")
            print(f"Chaves disponíveis: {list(data.keys())}")
            
            # Tenta diferentes nomes comuns para token
            possible_token_keys = [
                'access_token',
                'token',
                'accessToken',
                'jwt',
                'bearer',
                'auth_token',
                'authToken',
                'data.token',
                'data.access_token'
            ]
            
            print(f"\n[PROCURANDO TOKEN]")
            for key in possible_token_keys:
                if '.' in key:  # Nested key (ex: data.token)
                    parts = key.split('.')
                    value = data
                    for part in parts:
                        if isinstance(value, dict):
                            value = value.get(part)
                        else:
                            value = None
                            break
                    if value:
                        print(f"  ✓ Encontrado em '{key}': {value[:50]}...")
                else:
                    if key in data:
                        print(f"  ✓ Encontrado em '{key}': {data[key][:50]}...")
            
        except json.JSONDecodeError:
            print("❌ Resposta não é JSON válido")
        
        print(f"\n{'='*70}")
        
        if response.status_code == 200:
            print("✓ Autenticação SUCESSO (200 OK)")
            print("\nMas precisa ajustar o código para ler a chave correta!")
        elif response.status_code == 401:
            print("✗ Credenciais inválidas (401 Unauthorized)")
        elif response.status_code == 404:
            print("✗ Endpoint não encontrado (404)")
        else:
            print(f"? Status inesperado: {response.status_code}")
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO DE REQUISIÇÃO: {e}")
    
    print("="*70)

if __name__ == "__main__":
    debug_authentication()