#!/usr/bin/env python3
"""
PROBAR CONVERSIÓN DE DIVISAS
"""

import sys
import os

# Agregar el directorio actual al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend')

# Importar la función de conversión
from our_copytrading_api import convert_currency_format

def test_currency_conversion():
    """Probar conversión de divisas"""
    print("🔄 PROBANDO CONVERSIÓN DE DIVISAS")
    print("=" * 50)
    
    # Casos de prueba
    test_cases = [
        # Mercado real (deben convertirse a -op)
        ("EURUSD", "EURUSD-op"),
        ("GBPUSD", "GBPUSD-op"),
        ("USDJPY", "USDJPY-op"),
        ("AUDUSD", "AUDUSD-op"),
        
        # OTC (deben mantenerse igual)
        ("EURUSD-OTC", "EURUSD-OTC"),
        ("GBPUSD-OTC", "GBPUSD-OTC"),
        ("TRUMPUSD-OTC", "TRUMPUSD-OTC"),
        ("GOLD-OTC", "GOLD-OTC"),
        
        # Ya convertidas (deben mantenerse igual)
        ("EURUSD-op", "EURUSD-op"),
        ("GBPUSD-op", "GBPUSD-op"),
        
        # Otras divisas (deben mantenerse igual)
        ("BTCUSD", "BTCUSD"),
        ("ETHUSD", "ETHUSD"),
    ]
    
    print("🧪 Ejecutando pruebas de conversión...")
    print("-" * 50)
    
    all_passed = True
    
    for input_currency, expected_output in test_cases:
        result = convert_currency_format(input_currency)
        status = "✅" if result == expected_output else "❌"
        
        print(f"{status} {input_currency:15} → {result:15} (esperado: {expected_output})")
        
        if result != expected_output:
            all_passed = False
    
    print("-" * 50)
    
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("✅ La conversión de divisas funciona correctamente")
        print("✅ Maneja tanto -op como -OTC correctamente")
    else:
        print("❌ Algunas pruebas fallaron")
        print("🔧 Revisar la lógica de conversión")
    
    print("=" * 50)

if __name__ == "__main__":
    test_currency_conversion()





