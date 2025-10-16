#!/usr/bin/env python3
"""
Ferramenta de Descoberta de Endpoints da API Metaverso UFG
Testa diferentes combinações de URLs para encontrar a configuração correta
"""

import requests
import json
from typing import List, Dict, Tuple

class APIDiscovery:
    """Descobre URL base e estrutura da API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetaversoUFG-Discovery/1.0',
            'Accept': 'application/json'
        })
    
    def test_url_variants(self) -> List[Dict]:
        """Testa diferentes variações de URL base"""
        
        # Variações possíveis baseadas na documentação
        base_urls = [
            "https://mverso.space",           # Sem /v1
            "https://mverso.space/v1",        # Com /v1
            "https://mverso.space/api",       # Padrão alternativo
            "https://mverso.space/api/v1",    # API + versão
            "http://mverso.space",            # HTTP sem TLS (improvável)
            "https://api.mverso.space",       # Subdomínio api
            "https://api.mverso.space/v1",
        ]
        
        results = []
        
        print("="*70)
        print("DESCOBERTA DE URL BASE DA API")
        print("="*70)
        
        for base_url in base_urls:
            result = self._test_base_url(base_url)
            results.append(result)
            
            if result['status'] == 'OK':
                print(f"\n✓ SUCESSO: {base_url}")
                print(f"  Status: {result['http_code']}")
                print(f"  Resposta: {result['response_preview']}")
            elif result['status'] == 'REDIRECT':
                print(f"\n→ REDIRECT: {base_url}")
                print(f"  Para: {result['redirect_to']}")
            else:
                print(f"\n✗ FALHA: {base_url} ({result['error']})")
        
        return results
    
    def _test_base_url(self, base_url: str) -> Dict:
        """Testa se uma URL base responde"""
        try:
            response = self.session.get(
                base_url,
                timeout=10,
                allow_redirects=False  # Detecta redirects manualmente
            )
            
            if response.status_code == 200:
                return {
                    'url': base_url,
                    'status': 'OK',
                    'http_code': response.status_code,
                    'response_preview': response.text[:200]
                }
            elif response.status_code in [301, 302, 307, 308]:
                return {
                    'url': base_url,
                    'status': 'REDIRECT',
                    'http_code': response.status_code,
                    'redirect_to': response.headers.get('Location')
                }
            else:
                return {
                    'url': base_url,
                    'status': 'ERROR',
                    'http_code': response.status_code,
                    'error': f"HTTP {response.status_code}"
                }
                
        except requests.exceptions.Timeout:
            return {
                'url': base_url,
                'status': 'ERROR',
                'error': 'Timeout após 10s'
            }
        except requests.exceptions.ConnectionError:
            return {
                'url': base_url,
                'status': 'ERROR',
                'error': 'Conexão recusada'
            }
        except Exception as e:
            return {
                'url': base_url,
                'status': 'ERROR',
                'error': str(e)
            }
    
    def test_auth_endpoints(self, base_url: str) -> Dict:
        """Testa diferentes rotas de autenticação"""
        
        auth_paths = [
            "/v1/auth/login",
            "/auth/login",
            "/api/v1/auth/login",
            "/api/auth/login",
            "/login",
            "/v1/login",
        ]
        
        credentials = {
            "email": "scanner@example.com",
            "password": "scanner"
        }
        
        print(f"\n{'='*70}")
        print(f"TESTANDO ENDPOINTS DE AUTENTICAÇÃO EM: {base_url}")
        print(f"{'='*70}")
        
        results = {}
        
        for path in auth_paths:
            full_url = base_url + path
            try:
                response = self.session.post(
                    full_url,
                    json=credentials,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"\n✓ SUCESSO: {path}")
                    try:
                        data = response.json()
                        print(f"  Token recebido: {bool(data.get('access_token'))}")
                        results[path] = {
                            'status': 'OK',
                            'data': data
                        }
                    except:
                        print(f"  Resposta não é JSON")
                        results[path] = {
                            'status': 'OK',
                            'data': response.text[:200]
                        }
                elif response.status_code == 404:
                    print(f"✗ 404: {path} (não existe)")
                    results[path] = {'status': 'NOT_FOUND'}
                elif response.status_code == 401:
                    print(f"⚠ 401: {path} (credenciais inválidas, mas endpoint existe!)")
                    results[path] = {'status': 'UNAUTHORIZED'}
                elif response.status_code == 400:
                    print(f"⚠ 400: {path} (formato inválido, mas endpoint existe!)")
                    results[path] = {'status': 'BAD_REQUEST'}
                else:
                    print(f"? {response.status_code}: {path}")
                    results[path] = {
                        'status': f'HTTP_{response.status_code}'
                    }
                    
            except Exception as e:
                print(f"✗ ERRO: {path} ({e})")
                results[path] = {'status': 'ERROR', 'error': str(e)}
        
        return results
    
    def test_printer_endpoints(self, base_url: str, token: str = None) -> Dict:
        """Testa endpoints de impressora (se tiver token)"""
        
        printer_paths = [
            "/v1/printer/printable",
            "/printer/printable",
            "/api/v1/printer/printable",
            "/api/printer/printable",
        ]
        
        print(f"\n{'='*70}")
        print(f"TESTANDO ENDPOINTS DE IMPRESSORA")
        print(f"{'='*70}")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"Usando autenticação: Bearer {token[:20]}...")
        else:
            print("Testando sem autenticação (pode falhar com 401)")
        
        results = {}
        
        for path in printer_paths:
            full_url = base_url + path
            try:
                response = self.session.get(
                    full_url,
                    headers=headers,
                    params={"with_file": "false"},  # Sem arquivo por enquanto
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"\n✓ SUCESSO: {path}")
                    try:
                        data = response.json()
                        print(f"  Objetos na fila: {len(data) if isinstance(data, list) else 'N/A'}")
                        results[path] = {'status': 'OK', 'count': len(data) if isinstance(data, list) else None}
                    except:
                        print(f"  Resposta não é JSON")
                        results[path] = {'status': 'OK'}
                elif response.status_code == 404:
                    print(f"✗ 404: {path}")
                    results[path] = {'status': 'NOT_FOUND'}
                elif response.status_code == 401:
                    print(f"⚠ 401: {path} (precisa autenticação)")
                    results[path] = {'status': 'NEEDS_AUTH'}
                else:
                    print(f"? {response.status_code}: {path}")
                    results[path] = {'status': f'HTTP_{response.status_code}'}
                    
            except Exception as e:
                print(f"✗ ERRO: {path} ({e})")
                results[path] = {'status': 'ERROR', 'error': str(e)}
        
        return results
    
    def run_full_discovery(self):
        """Executa descoberta completa"""
        print("\n" + "="*70)
        print("INICIANDO DESCOBERTA COMPLETA DA API METAVERSO UFG")
        print("="*70 + "\n")
        
        # Passo 1: Descobre URL base
        base_results = self.test_url_variants()
        
        # Encontra URLs que funcionaram
        working_bases = [r for r in base_results if r['status'] in ['OK', 'REDIRECT']]
        
        if not working_bases:
            print("\n" + "="*70)
            print("❌ NENHUMA URL BASE RESPONDEU")
            print("="*70)
            print("\nPossíveis causas:")
            print("1. Servidor offline")
            print("2. Problema de rede/firewall")
            print("3. Domínio incorreto")
            print("\nVerifique:")
            print("- Consegue acessar https://mverso.space no navegador?")
            print("- Está na rede da UFG?")
            return
        
        # Testa autenticação em cada URL que respondeu
        for base in working_bases:
            base_url = base['url']
            
            if base['status'] == 'REDIRECT':
                base_url = base['redirect_to']
                print(f"\nSeguindo redirect para: {base_url}")
            
            auth_results = self.test_auth_endpoints(base_url)
            
            # Se encontrou endpoint de autenticação que funciona
            working_auth = {k: v for k, v in auth_results.items() if v['status'] == 'OK'}
            
            if working_auth:
                path, data = list(working_auth.items())[0]
                token = data['data'].get('access_token')
                
                print(f"\n{'='*70}")
                print(f"✓ CONFIGURAÇÃO ENCONTRADA!")
                print(f"{'='*70}")
                print(f"URL Base: {base_url}")
                print(f"Endpoint Auth: {path}")
                print(f"Token obtido: {token[:30] if token else 'N/A'}...")
                
                # Testa endpoints de impressora
                self.test_printer_endpoints(base_url, token)
                
                print(f"\n{'='*70}")
                print(f"RESUMO DA CONFIGURAÇÃO CORRETA")
                print(f"{'='*70}")
                print(f"\nAtualize o arquivo metaverso_api_client.py:")
                print(f"\n@dataclass")
                print(f"class PrinterConfig:")
                print(f'    base_url: str = "{base_url}"')
                print(f'    # Resto permanece igual...')
                print(f"\n{'='*70}\n")
                
                return
        
        # Se chegou aqui, não encontrou autenticação funcionando
        print(f"\n{'='*70}")
        print(f"⚠ URL BASE ENCONTRADA, MAS AUTENTICAÇÃO FALHOU")
        print(f"{'='*70}")
        print(f"\nVerifique:")
        print(f"1. Credenciais corretas (email/senha)")
        print(f"2. Estrutura do endpoint de autenticação")
        print(f"3. Documentação da API atualizada")


if __name__ == "__main__":
    discovery = APIDiscovery()
    discovery.run_full_discovery()