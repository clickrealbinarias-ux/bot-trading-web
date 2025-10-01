#!/usr/bin/env python3
"""
Monitor de logs CORREGIDO para el sistema de copytrading
Puerto 5001 (sin conflicto con AirPlay)
"""

import requests
import time
import subprocess
from datetime import datetime

def monitor_system():
    """Monitor del sistema corregido"""
    print("🔍 MONITOR DE COPYTRADING - VERSIÓN CORREGIDA")
    print("=" * 60)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Puerto corregido: 5001 (sin conflicto AirPlay)")
    print("=" * 60)
    
    # Verificar estado del sistema
    try:
        response = requests.get("http://localhost:5001/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend (puerto 5001): FUNCIONANDO")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Backend (puerto 5001): ERROR {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend (puerto 5001): NO DISPONIBLE - {e}")
        return False
    
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend (puerto 8000): FUNCIONANDO")
        else:
            print(f"❌ Frontend (puerto 8000): ERROR {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend (puerto 8000): NO DISPONIBLE - {e}")
    
    print("\n🎯 INSTRUCCIONES:")
    print("1. Abre http://localhost:8000 en tu navegador")
    print("2. Configura tu cuenta de trader con credenciales de ExNova")
    print("3. Agrega las cuentas de seguidores")
    print("4. Activa el monitoreo automático")
    print("5. Ejecuta una entrada en ExNova")
    print("6. Observa los logs aquí en tiempo real")
    
    print("\n⏳ MONITOREANDO ACTIVIDAD...")
    print("🛑 Presiona Ctrl+C para detener")
    print("-" * 60)
    
    # Monitoreo continuo
    while True:
        try:
            # Verificar estado de la API
            response = requests.get("http://localhost:5001/api/status", timeout=2)
            if response.status_code == 200:
                # API funcionando, continuar monitoreo
                pass
            else:
                print(f"⚠️  API respondió con código: {response.status_code}")
        except Exception as e:
            print(f"⚠️  Error conectando a la API: {e}")
            break
        
        time.sleep(1)

if __name__ == "__main__":
    try:
        monitor_system()
    except KeyboardInterrupt:
        print("\n🛑 Monitor detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error en el monitor: {e}")

