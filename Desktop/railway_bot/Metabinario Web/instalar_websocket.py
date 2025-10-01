#!/usr/bin/env python3
"""
Script para instalar websocket-client correctamente
"""

import subprocess
import sys
import os

print("🔧 INSTALANDO WEBSOCKET-CLIENT...")
print("=" * 50)

# Cambiar al directorio correcto
os.chdir("/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web")

# Activar entorno virtual y instalar
try:
    # Instalar websocket-client
    result = subprocess.run([
        sys.executable, '-m', 'pip', 'install', 'websocket-client==1.6.4'
    ], capture_output=True, text=True, cwd="/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web")
    
    print(f"📦 Resultado instalación: {result.returncode}")
    print(f"📝 Salida: {result.stdout}")
    if result.stderr:
        print(f"❌ Errores: {result.stderr}")
    
    # Verificar instalación
    print("\n🔍 VERIFICANDO INSTALACIÓN...")
    try:
        import websocket
        print(f"✅ websocket importado desde: {websocket.__file__}")
        
        # Probar WebSocketApp
        ws = websocket.WebSocketApp('ws://test')
        print(f"✅ WebSocketApp creado")
        print(f"✅ run_forever disponible: {hasattr(ws, 'run_forever')}")
        
        if hasattr(ws, 'run_forever'):
            print("🎉 ¡WEBSOCKET INSTALADO CORRECTAMENTE!")
        else:
            print("⚠️ WebSocketApp no tiene run_forever")
            
    except ImportError as e:
        print(f"❌ Error importando websocket: {e}")
    except Exception as e:
        print(f"❌ Error con WebSocketApp: {e}")
        
except Exception as e:
    print(f"❌ Error ejecutando pip: {e}")

print("\n" + "=" * 50)
print("🎯 INSTALACIÓN COMPLETADA")