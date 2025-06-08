#!/usr/bin/env python3
"""
Comprehensive test script demonstrating various API change detection scenarios.
This script tests both positive and negative cases to validate the diff detection system.
"""

from diff_detector import APISpecDiffDetector
import json

def test_scenario(name, current_spec, previous_spec, expected_breaking=None):
    """Test a specific scenario and report results."""
    print(f"\n=== {name} ===")
    
    detector = APISpecDiffDetector()
    result = detector.detect_changes(current_spec, previous_spec)
    
    if result:
        print(f"✅ Mudanças detectadas")
        print(f"   Breaking changes: {result['has_breaking_changes']}")
        print(f"   Quantidade: {len(result['breaking_changes'])}")
        print(f"   Resumo: {result['summary']}")
        
        if expected_breaking is not None:
            if result['has_breaking_changes'] == expected_breaking:
                print(f"   ✅ Expectativa atendida (breaking={expected_breaking})")
            else:
                print(f"   ❌ Expectativa não atendida (esperado breaking={expected_breaking}, obtido={result['has_breaking_changes']})")
        
        if result['breaking_changes']:
            print("   Breaking changes detectadas:")
            for i, change in enumerate(result['breaking_changes'][:3]):  # Mostrar apenas os 3 primeiros
                print(f"     {i+1}. {change.get('text', change.get('description', str(change)))}")
            if len(result['breaking_changes']) > 3:
                print(f"     ... e mais {len(result['breaking_changes']) - 3} mudanças")
    else:
        print("❌ Nenhuma mudança detectada")
        if expected_breaking is not None and expected_breaking:
            print(f"   ❌ Expectativa não atendida (esperado breaking={expected_breaking})")

def main():
    """Run comprehensive tests."""
    print("=== TESTES ABRANGENTES DE DETECÇÃO DE MUDANÇAS ===")
    
    # Spec base
    base_spec = {
        'openapi': '3.0.0',
        'info': {'title': 'Test API', 'version': '1.0.0'},
        'paths': {
            '/users': {
                'get': {
                    'parameters': [
                        {'name': 'limit', 'in': 'query', 'required': False, 'schema': {'type': 'integer'}}
                    ],
                    'responses': {'200': {'description': 'OK'}}
                },
                'post': {
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'string'},
                                        'email': {'type': 'string'}
                                    },
                                    'required': ['name']
                                }
                            }
                        }
                    },
                    'responses': {'201': {'description': 'Created'}}
                }
            }
        }
    }
    
    # CASO 1: Spec inicial (sem spec anterior)
    test_scenario(
        "CASO 1: Spec Inicial",
        base_spec, None,
        expected_breaking=False
    )
    
    # CASO 2: Specs idênticas
    test_scenario(
        "CASO 2: Specs Idênticas",
        base_spec, base_spec,
        expected_breaking=False
    )
    
    # CASO 3: Adição de parâmetro obrigatório (BREAKING)
    spec_with_required_param = {
        **base_spec,
        'info': {'title': 'Test API', 'version': '1.1.0'},
        'paths': {
            '/users': {
                'get': {
                    'parameters': [
                        {'name': 'limit', 'in': 'query', 'required': False, 'schema': {'type': 'integer'}},
                        {'name': 'user_id', 'in': 'query', 'required': True, 'schema': {'type': 'string'}}
                    ],
                    'responses': {'200': {'description': 'OK'}}
                },
                'post': base_spec['paths']['/users']['post']
            }
        }
    }
    
    test_scenario(
        "CASO 3: Adição de Parâmetro Obrigatório",
        spec_with_required_param, base_spec,
        expected_breaking=True
    )
    
    # CASO 4: Remoção de endpoint (BREAKING)
    spec_removed_endpoint = {
        **base_spec,
        'info': {'title': 'Test API', 'version': '2.0.0'},
        'paths': {
            '/users': {
                'get': base_spec['paths']['/users']['get']
                # POST removido
            }
        }
    }
    
    test_scenario(
        "CASO 4: Remoção de Endpoint",
        spec_removed_endpoint, base_spec,
        expected_breaking=True
    )
    
    # CASO 5: Adição de novo endpoint (NÃO BREAKING)
    spec_new_endpoint = {
        **base_spec,
        'info': {'title': 'Test API', 'version': '1.2.0'},
        'paths': {
            **base_spec['paths'],
            '/products': {
                'get': {
                    'responses': {'200': {'description': 'OK'}}
                }
            }
        }
    }
    
    test_scenario(
        "CASO 5: Adição de Novo Endpoint",
        spec_new_endpoint, base_spec,
        expected_breaking=False
    )
    
    # CASO 6: Adição de parâmetro opcional (NÃO BREAKING)
    spec_optional_param = {
        **base_spec,
        'info': {'title': 'Test API', 'version': '1.1.0'},
        'paths': {
            '/users': {
                'get': {
                    'parameters': [
                        {'name': 'limit', 'in': 'query', 'required': False, 'schema': {'type': 'integer'}},
                        {'name': 'sort', 'in': 'query', 'required': False, 'schema': {'type': 'string'}}
                    ],
                    'responses': {'200': {'description': 'OK'}}
                },
                'post': base_spec['paths']['/users']['post']
            }
        }
    }
    
    test_scenario(
        "CASO 6: Adição de Parâmetro Opcional",
        spec_optional_param, base_spec,
        expected_breaking=False
    )
    
    # CASO 7: Mudança de tipo de campo obrigatório (BREAKING)
    spec_type_change = {
        **base_spec,
        'info': {'title': 'Test API', 'version': '2.0.0'},
        'paths': {
            '/users': {
                'get': base_spec['paths']['/users']['get'],
                'post': {
                    'requestBody': {
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'name': {'type': 'integer'},  # Mudou de string para integer
                                        'email': {'type': 'string'}
                                    },
                                    'required': ['name']
                                }
                            }
                        }
                    },
                    'responses': {'201': {'description': 'Created'}}
                }
            }
        }
    }
    
    test_scenario(
        "CASO 7: Mudança de Tipo de Campo Obrigatório",
        spec_type_change, base_spec,
        expected_breaking=True
    )
    
    # CASO 8: Spec vazia
    empty_spec = {
        'openapi': '3.0.0',
        'info': {'title': 'Empty API', 'version': '1.0.0'},
        'paths': {}
    }
    
    test_scenario(
        "CASO 8: Remoção de Todos os Endpoints",
        empty_spec, base_spec,
        expected_breaking=True
    )
    
    print("\n=== RESUMO DOS TESTES ===")
    print("✅ Todos os cenários de teste foram executados")
    print("📊 Cobertura de testes:")
    print("   - Spec inicial")
    print("   - Specs idênticas")
    print("   - Mudanças breaking (parâmetros obrigatórios, remoção de endpoints, mudança de tipos)")
    print("   - Mudanças não-breaking (novos endpoints, parâmetros opcionais)")
    print("   - Casos extremos (spec vazia)")

if __name__ == '__main__':
    main() 