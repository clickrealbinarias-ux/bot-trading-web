#!/usr/bin/env python3
"""
Diagnóstico completo del sistema Metabinario Web
"""

import sys
import os
import subprocess

print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA METABINARIO WEB")
print("=" * 60)

# 1. Verificar Python
print("\n1️⃣ VERIFICANDO PYTHON:")
print(f"   Python: {sys.version}")
print(f"   Ejecutable: {sys.executable}")

# 2. Verificar entorno virtual
print("\n2️⃣ VERIFICANDO ENTORNO VIRTUAL:")
venv_path = "/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/venv"
if os.path.exists(venv_path):
    print(f"   ✅ Entorno virtual encontrado: {venv_path}")
else:
    print(f"   ❌ Entorno virtual NO encontrado: {venv_path}")

# 3. Verificar dependencias
print("\n3️⃣ VERIFICANDO DEPENDENCIAS:")
deps = [
    'Flask', 'Flask-SocketIO', 'Flask-CORS', 'PyJWT', 
    'python-socketio', 'eventlet', 'requests', 'websockets', 'websocket-client'
]

for dep in deps:
    try:
        __import__(dep.replace('-', '_'))
        print(f"   ✅ {dep}")
    except ImportError:
        print(f"   ❌ {dep} - FALTANTE")

# 4. Verificar websocket específicamente
print("\n4️⃣ VERIFICANDO WEBSOCKET:")
try:
    import websocket
    print(f"   ✅ websocket importado desde: {websocket.__file__}")
    
    # Probar WebSocketApp
    ws = websocket.WebSocketApp('ws://test')
    print(f"   ✅ WebSocketApp creado")
    print(f"   ✅ run_forever disponible: {hasattr(ws, 'run_forever')}")
    
except ImportError as e:
    print(f"   ❌ Error importando websocket: {e}")
except Exception as e:
    print(f"   ❌ Error con WebSocketApp: {e}")

# 5. Verificar ExNova API
print("\n5️⃣ VERIFICANDO EXNOVA API:")
exnova_path = "/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi"
if os.path.exists(exnova_path):
    print(f"   ✅ ExNova API encontrada: {exnova_path}")
    
    # Agregar al path
    sys.path.append(exnova_path)
    
    try:
        from exnovaapi.ws.client import ExNovaWebSocketClient
        print(f"   ✅ ExNovaWebSocketClient importado correctamente")
    except ImportError as e:
        print(f"   ❌ Error importando ExNovaWebSocketClient: {e}")
else:
    print(f"   ❌ ExNova API NO encontrada: {exnova_path}")

# 6. Verificar puertos
print("\n6️⃣ VERIFICANDO PUERTOS:")
import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

ports = [5000, 5001, 5003, 8000]
for port in ports:
    if check_port(port):
        print(f"   ⚠️  Puerto {port} - OCUPADO")
    else:
        print(f"   ✅ Puerto {port} - DISPONIBLE")

print("\n" + "=" * 60)
print("🎯 DIAGNÓSTICO COMPLETADO")

