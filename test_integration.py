#!/usr/bin/env python3
"""
Integration test to verify the diff detection system is working correctly.
"""

from diff_detector import APISpecDiffDetector
import json

def test_integration():
    """Test practical diff detection."""
    print("=== TESTE DE INTEGRAÇÃO ===")
    
    # Spec inicial
    spec1 = {
        'openapi': '3.0.0',
        'info': {'title': 'Test API', 'version': '1.0.0'},
        'paths': {
            '/users': {
                'get': {'responses': {'200': {'description': 'OK'}}}
            }
        }
    }

    # Spec com parâmetro obrigatório adicionado
    spec2 = {
        'openapi': '3.0.0',
        'info': {'title': 'Test API', 'version': '2.0.0'},
        'paths': {
            '/users': {
                'get': {
                    'parameters': [{'name': 'id', 'in': 'query', 'required': True, 'schema': {'type': 'string'}}],
                    'responses': {'200': {'description': 'OK'}}
                }
            }
        }
    }

    detector = APISpecDiffDetector()
    result = detector.detect_changes(spec2, spec1)
    
    if result:
        print('✅ MUDANÇAS DETECTADAS')
        print(f'Mudanças breaking: {result["has_breaking_changes"]}')
        print(f'Quantidade de breaking changes: {len(result["breaking_changes"])}')
        print(f'Resumo: {result["summary"]}')
        if result['breaking_changes']:
            print('Breaking changes detectadas:')
            for change in result['breaking_changes']:
                print(f'  - {change}')
        if result['changelog']:
            print('\nChangelog:')
            print(result['changelog'])
    else:
        print('❌ Nenhuma mudança detectada')

    # Teste com specs idênticas
    print("\n=== TESTE COM SPECS IDÊNTICAS ===")
    result_identical = detector.detect_changes(spec1, spec1)
    if result_identical is None:
        print('✅ Specs idênticas corretamente detectadas (retorno None)')
    else:
        print('❌ Erro: specs idênticas não foram detectadas corretamente')

    # Teste com spec inicial
    print("\n=== TESTE COM SPEC INICIAL ===")
    result_initial = detector.detect_changes(spec1, None)
    if result_initial:
        print('✅ Spec inicial corretamente processada')
        print(f'Resumo: {result_initial["summary"]}')
        print(f'Breaking changes: {result_initial["has_breaking_changes"]}')
    else:
        print('❌ Erro: spec inicial não foi processada corretamente')

if __name__ == '__main__':
    test_integration() 