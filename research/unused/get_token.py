#!/usr/bin/env python3
"""
Gerador de Token Rápido
Cria token e salva em arquivo para uso posterior
"""

import requests
import json
from datetime import datetime

def get_token():
    """Gera token e exibe na tela"""
    
    url = "https://metaverso.medialab.ufg.br/v1/auth/login"
    
    # Tenta com diferentes payloads
    payloads = [
        {"email": "scanner@example.com", "password": "scanner"},
        {"email": "scanner@example.com", "username": "scanner", "password": "scanner"},
        {"username": "scanner", "password": "scanner"},
    ]
    
    print("="*70)
    print("GERADOR DE TOKEN - API METAVERSO UFG")
    print("="*70)
    
    for i, payload in enumerate(payloads, 1):
        print(f"\n[Tentativa {i}] Payload: {json.dumps(payload)}")
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✓✓✓ SUCESSO! ✓✓✓\n")
                print(json.dumps(data, indent=2))
                
                # Procura token
                token = None
                for key in ['access_token', 'token', 'accessToken', 'jwt']:
                    if key in data:
                        token = data[key]
                        break
                
                if token:
                    print(f"\n{'='*70}")
                    print("TOKEN GERADO:")
                    print(f"{'='*70}")
                    print(token)
                    print(f"{'='*70}\n")
                    
                    # Salva em arquivo
                    with open("token.txt", "w") as f:
                        f.write(f"Token gerado em: {datetime.now()}\n")
                        f.write(f"Token: {token}\n")
                        f.write(f"\nPayload usado:\n{json.dumps(payload, indent=2)}\n")
                    
                    print("✓ Token salvo em: token.txt")
                    
                    # Salva configuração para usar no código
                    config = {
                        "base_url": "https://metaverso.medialab.ufg.br/v1",
                        "payload": payload,
                        "token_key": key
                    }
                    with open("api_config.json", "w") as f:
                        json.dump(config, f, indent=2)
                    
                    print("✓ Configuração salva em: api_config.json")
                    
                    return token, payload
                else:
                    print("⚠ Autenticação sucesso mas token não encontrado")
                    print(f"Chaves disponíveis: {list(data.keys())}")
                    
            elif response.status_code == 401:
                print("✗ Credenciais inválidas")
                print(f"Resposta: {response.text}")
            elif response.status_code == 404:
                print("✗ Endpoint não existe")
            else:
                print(f"? Status inesperado")
                print(f"Resposta: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("✗ Timeout - verifique conexão com rede UFG")
        except requests.exceptions.ConnectionError:
            print("✗ Erro de conexão - servidor inacessível")
        except Exception as e:
            print(f"✗ Erro: {e}")
    
    print("\n" + "="*70)
    print("❌ FALHA EM TODAS AS TENTATIVAS")
    print("="*70)
    print("\nVerifique:")
    print("1. Está na rede da UFG?")
    print("2. Credenciais corretas?")
    print("3. Usuário 'scanner' foi criado?")
    return None, None

if __name__ == "__main__":
    token, payload = get_token()
    
    if token:
        print("\n" + "="*70)
        print("COMO USAR NO CÓDIGO:")
        print("="*70)
        print("\n# Opção 1: Carregando do arquivo")
        print("with open('token.txt', 'r') as f:")
        print("    lines = f.readlines()")
        print("    token = lines[1].split('Token: ')[1].strip()")
        print("\n# Opção 2: Usando configuração salva")
        print("import json")
        print("with open('api_config.json', 'r') as f:")
        print("    config = json.load(f)")
        print("    # config['payload'] tem o formato correto")
        print("="*70)