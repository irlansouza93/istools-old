# -*- coding: utf-8 -*-
"""
Script de Teste para o Sistema de Tradução Bilíngue
Baseado nas regras do arquivo newrules
"""

import sys
import os

# Adiciona o diretório do plugin ao path para importar os módulos
plugin_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, plugin_dir)

from translations.translate import translate

def test_translation_system():
    """
    Testa o sistema de tradução bilíngue com diferentes cenários
    """
    print("=== TESTE DO SISTEMA DE TRADUÇÃO BILÍNGUE ===\n")
    
    # Teste 1: Tradução para português
    print("1. Teste para português (pt):")
    result_pt = translate(("Extend Lines", "Estender Linhas"), "pt")
    print(f"   Input: ('Extend Lines', 'Estender Linhas')")
    print(f"   Locale: pt")
    print(f"   Output: {result_pt}")
    print(f"   Esperado: Estender Linhas")
    print(f"   Status: {'✓ PASSOU' if result_pt == 'Estender Linhas' else '✗ FALHOU'}\n")
    
    # Teste 2: Tradução para inglês
    print("2. Teste para inglês (en):")
    result_en = translate(("Extend Lines", "Estender Linhas"), "en")
    print(f"   Input: ('Extend Lines', 'Estender Linhas')")
    print(f"   Locale: en")
    print(f"   Output: {result_en}")
    print(f"   Esperado: Extend Lines")
    print(f"   Status: {'✓ PASSOU' if result_en == 'Extend Lines' else '✗ FALHOU'}\n")
    
    # Teste 3: String única em português
    print("3. Teste string única para português:")
    result_single_pt = translate("ISTools", "pt")
    print(f"   Input: 'ISTools'")
    print(f"   Locale: pt")
    print(f"   Output: {result_single_pt}")
    print(f"   Esperado: ISTools")
    print(f"   Status: {'✓ PASSOU' if result_single_pt == 'ISTools' else '✗ FALHOU'}\n")
    
    # Teste 4: String única em inglês
    print("4. Teste string única para inglês:")
    result_single_en = translate("ISTools", "en")
    print(f"   Input: 'ISTools'")
    print(f"   Locale: en")
    print(f"   Output: {result_single_en}")
    print(f"   Esperado: ISTools")
    print(f"   Status: {'✓ PASSOU' if result_single_en == 'ISTools' else '✗ FALHOU'}\n")
    
    # Teste 5: Idioma não suportado (fallback)
    print("5. Teste idioma não suportado (fallback):")
    result_fallback = translate(("Polygon Generator", "Gerador de Polígonos"), "zh")
    print(f"   Input: ('Polygon Generator', 'Gerador de Polígonos')")
    print(f"   Locale: zh")
    print(f"   Output: {result_fallback}")
    print(f"   Esperado: Polygon Generator (fallback para inglês)")
    print(f"   Status: {'✓ PASSOU' if result_fallback == 'Polygon Generator' else '✗ FALHOU'}\n")
    
    # Teste 6: Teste com dicionário (espanhol)
    print("6. Teste com dicionário (espanhol):")
    result_es = translate(("Tools", "Ferramentas"), "es")
    print(f"   Input: ('Tools', 'Ferramentas')")
    print(f"   Locale: es")
    print(f"   Output: {result_es}")
    print(f"   Esperado: Herramientas (do dicionário)")
    print(f"   Status: {'✓ PASSOU' if result_es == 'Herramientas' else '✗ FALHOU'}\n")
    
    # Teste 7: Teste com múltiplos argumentos (como usado no plugin)
    print("7. Teste com múltiplos argumentos:")
    # Simula como o método tr() do plugin chama a função translate
    args = ("Point on Surface Generator", "Gerador de Pontos na Superfície")
    result_multi = translate(args, "pt")
    print(f"   Input: {args}")
    print(f"   Locale: pt")
    print(f"   Output: {result_multi}")
    print(f"   Esperado: Gerador de Pontos na Superfície")
    print(f"   Status: {'✓ PASSOU' if result_multi == 'Gerador de Pontos na Superfície' else '✗ FALHOU'}\n")
    
    print("=== FIM DOS TESTES ===")

def test_plugin_integration():
    """
    Testa a integração com os módulos do plugin
    """
    print("\n=== TESTE DE INTEGRAÇÃO COM MÓDULOS DO PLUGIN ===\n")
    
    try:
        # Simula a importação dos módulos do plugin
        from polygon_generator import QgisPolygonGenerator
        from extend_lines import ExtendLines
        from point_on_surface_generator import PointOnSurfaceGenerator
        from bounded_polygon_generator import BoundedPolygonGenerator
        
        print("✓ Todos os módulos foram importados com sucesso")
        print("✓ O novo sistema de tradução está integrado")
        
    except ImportError as e:
        print(f"✗ Erro na importação: {e}")
        print("  Nota: Este erro é esperado se executado fora do ambiente QGIS")
    
    print("\n=== FIM DO TESTE DE INTEGRAÇÃO ===")

if __name__ == "__main__":
    test_translation_system()
    test_plugin_integration()