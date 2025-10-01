#!/usr/bin/env python3
"""
Script de diagnóstico para Metabinario Web
Verifica el estado del sistema de copytrading
"""

import requests
import json
import sys

def test_api():
    """Probar la API del backend"""
    print("🔍 Diagnosticando Metabinario Web...")
    print("=" * 50)
    
    # Probar puerto 5000
    try:
        response = requests.get("http://localhost:5000/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend en puerto 5000: FUNCIONANDO")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Backend en puerto 5000: ERROR {response.status_code}")
    except Exception as e:
        print(f"❌ Backend en puerto 5000: NO DISPONIBLE - {e}")
    
    # Probar puerto 5003
    try:
        response = requests.get("http://localhost:5003/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend en puerto 5003: FUNCIONANDO")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Backend en puerto 5003: ERROR {response.status_code}")
    except Exception as e:
        print(f"❌ Backend en puerto 5003: NO DISPONIBLE - {e}")
    
    print("\n" + "=" * 50)
    print("📋 INSTRUCCIONES PARA CONFIGURAR COPYTRADING:")
    print("=" * 50)
    print("1. Abre tu navegador en: http://localhost:8000")
    print("2. Inicia sesión como TRADER con tus credenciales de ExNova")
    print("3. Agrega tu cuenta de trader en la sección 'Trader'")
    print("4. Agrega las cuentas de seguidores en la sección 'Seguidores'")
    print("5. Inicia el monitoreo automático desde el panel de trader")
    print("\n⚠️  IMPORTANTE:")
    print("- Necesitas credenciales REALES de ExNova")
    print("- Las cuentas deben estar en modo PRACTICE o REAL")
    print("- El monitoreo debe estar ACTIVADO")
    print("\n🔧 Si el problema persiste:")
    print("- Verifica que las credenciales de ExNova sean correctas")
    print("- Asegúrate de que el monitoreo automático esté iniciado")
    print("- Revisa los logs del backend para errores específicos")

if __name__ == "__main__":
    test_api()

