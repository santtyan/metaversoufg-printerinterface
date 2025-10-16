#!/usr/bin/env python3
"""
Descoberta de Endpoints: mverso.space
Testa múltiplas combinações para encontrar estrutura correta
"""

import requests
import json

def test_auth_variations():
    """Testa diferentes estruturas de autenticação"""
    
    base_url = "https://mverso.space"
    
    # Variações de endpoint de autenticação
    auth_endpoints = [
        "/v1/auth/login",
        "/auth/login",
        "/api/v1/auth/login",
        "/api/auth/login",
        "/login",
        "/v1/login",
        "/users/login",
        "/v1/users/login",
    ]
    
    # Variações de payload
    payloads = [
        # Payload 1: Email + Password
        {
            "email": "scanner@example.com",
            "password": "scanner"
        },
        # Payload 2: Username + Password
        {
            "username": "scanner",
            "password": "scanner"
        },
        # Payload 3: Email + Username + Password (do WhatsApp)
        {
            "email": "scanner@example.com",
            "username": "scanner",
            "password": "scanner"
        },
    ]
    
    print("="*70)
    print("DESCOBERTA DE ENDPOINT DE AUTENTICAÇÃO - mverso.space")
    print("="*70)
    
    for endpoint in auth_endpoints:
        for i, payload in enumerate(payloads, 1):
            url = base_url + endpoint
            
            print(f"\n[TESTE] {url}")
            print(f"Payload {i}: {json.dumps(payload, indent=2)}")
            
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("✓✓✓ SUCESSO! ✓✓✓")
                    try:
                        data = response.json()
                        print(f"Resposta:")
                        print(json.dumps(data, indent=2, ensure_ascii=False))
                        
                        # Procura token
                        print(f"\n[PROCURANDO TOKEN]")
                        for key in data.keys():
                            if 'token' in key.lower() or 'access' in key.lower():
                                print(f"  Token encontrado em '{key}': {data[key][:50]}...")
                        
                        print(f"\n{'='*70}")
                        print(f"CONFIGURAÇÃO CORRETA ENCONTRADA!")
                        print(f"{'='*70}")
                        print(f"URL: {url}")
                        print(f"Payload: {json.dumps(payload, indent=2)}")
                        print(f"{'='*70}\n")
                        
                        return url, payload, data
                        
                    except json.JSONDecodeError:
                        print(f"Resposta não é JSON: {response.text[:200]}")
                        
                elif response.status_code == 404:
                    print("✗ 404: Endpoint não existe")
                elif response.status_code == 401:
                    print("⚠ 401: Credenciais inválidas (mas endpoint EXISTE!)")
                    print(f"Resposta: {response.text[:200]}")
                elif response.status_code == 400:
                    print("⚠ 400: Formato inválido (mas endpoint EXISTE!)")
                    print(f"Resposta: {response.text[:200]}")
                else:
                    print(f"? Status {response.status_code}")
                    print(f"Resposta: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print("✗ Timeout")
            except requests.exceptions.ConnectionError:
                print("✗ Erro de conexão")
            except Exception as e:
                print(f"✗ Erro: {e}")
    
    print("\n" + "="*70)
    print("❌ NENHUMA COMBINAÇÃO FUNCIONOU")
    print("="*70)
    return None, None, None

def test_base_url():
    """Testa se servidor está acessível"""
    print("\n[TESTE INICIAL] Verificando se mverso.space está online...")
    
    urls = [
        "https://mverso.space",
        "https://mverso.space/v1",
        "https://mverso.space/api",
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"  {url} → Status {response.status_code}")
            if response.status_code == 200:
                print(f"  Resposta: {response.text[:200]}")
        except Exception as e:
            print(f"  {url} → Erro: {e}")

def test_swagger_docs():
    """Procura documentação Swagger/OpenAPI"""
    print("\n[PROCURANDO DOCUMENTAÇÃO]")
    
    doc_paths = [
        "/docs",
        "/swagger",
        "/api-docs",
        "/v1/docs",
        "/openapi.json",
        "/swagger.json",
    ]
    
    for path in doc_paths:
        url = f"https://mverso.space{path}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"  ✓ Documentação encontrada: {url}")
                print(f"    Acesse no navegador para ver endpoints disponíveis")
        except:
            pass

if __name__ == "__main__":
    # Teste 1: Servidor online?
    test_base_url()
    
    # Teste 2: Documentação disponível?
    test_swagger_docs()
    
    # Teste 3: Descobre autenticação
    url, payload, data = test_auth_variations()
    
    if url:
        print("\n✓ Sucesso! Use esta configuração no código.")
    else:
        print("\n❌ Falha. Possíveis próximos passos:")
        print("1. Contate Guilherme para confirmar credenciais")
        print("2. Peça acesso ao Swagger/documentação atualizada")
        print("3. Verifique se há autenticação via OAuth/API Key")