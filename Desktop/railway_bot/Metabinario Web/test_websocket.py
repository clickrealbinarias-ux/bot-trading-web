#!/usr/bin/env python3
"""
Script de prueba para verificar websocket
"""

import sys
import os

# Agregar el directorio exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

print("🔍 Probando importación de websocket...")

try:
    import websocket
    print("✅ websocket importado correctamente")
    print(f"📦 Ubicación: {websocket.__file__}")
except ImportError as e:
    print(f"❌ Error importando websocket: {e}")
    
    # Intentar instalar
    print("🔧 Intentando instalar websocket-client...")
    import subprocess
    result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'websocket-client'], 
                          capture_output=True, text=True)
    print(f"📦 Resultado instalación: {result.returncode}")
    print(f"📝 Salida: {result.stdout}")
    print(f"❌ Errores: {result.stderr}")
    
    # Intentar importar nuevamente
    try:
        import websocket
        print("✅ websocket importado después de instalación")
    except ImportError as e2:
        print(f"❌ Error persistente: {e2}")

print("🔍 Probando importación desde exnovaapi...")
try:
    from exnovaapi.ws.client import ExNovaWebSocketClient
    print("✅ ExNovaWebSocketClient importado correctamente")
except ImportError as e:
    print(f"❌ Error importando ExNovaWebSocketClient: {e}")

