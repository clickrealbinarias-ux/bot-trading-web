#!/usr/bin/env python3
"""
Script para restaurar el sistema Metabinario Web según la documentación
"""

import subprocess
import time
import os
import signal
import sys

def kill_all_processes():
    """Detener todos los procesos relacionados"""
    print("🧹 Limpiando procesos existentes...")
    
    # Detener procesos Python
    subprocess.run(['pkill', '-f', 'python.*run.py'], capture_output=True)
    subprocess.run(['pkill', '-f', 'http.server'], capture_output=True)
    subprocess.run(['pkill', '-f', 'simple_server'], capture_output=True)
    
    # Liberar puertos
    subprocess.run(['lsof', '-ti:5000,5001,5003,8000'], capture_output=True)
    
    time.sleep(2)
    print("✅ Procesos detenidos")

def start_backend():
    """Iniciar backend en puerto 5003 según documentación"""
    print("🚀 Iniciando backend en puerto 5003...")
    
    # Cambiar al directorio backend
    os.chdir('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend')
    
    # Activar entorno virtual y ejecutar
    cmd = 'source ../venv/bin/activate && python3 run.py'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Esperar que se inicie
    time.sleep(5)
    
    # Verificar que esté funcionando
    try:
        import requests
        response = requests.get('http://localhost:5003/api/status', timeout=5)
        if response.status_code == 200:
            print("✅ Backend iniciado correctamente en puerto 5003")
            return True
        else:
            print(f"❌ Backend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando backend: {e}")
        return False

def start_frontend():
    """Iniciar frontend en puerto 8000"""
    print("🌐 Iniciando frontend en puerto 8000...")
    
    # Cambiar al directorio frontend
    os.chdir('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/frontend')
    
    # Usar servidor simple y robusto
    cmd = 'python3 -m http.server 8000'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Esperar que se inicie
    time.sleep(3)
    
    # Verificar que esté funcionando
    try:
        import requests
        response = requests.get('http://localhost:8000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend iniciado correctamente en puerto 8000")
            return True
        else:
            print(f"❌ Frontend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando frontend: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 RESTAURANDO SISTEMA METABINARIO WEB")
    print("=" * 50)
    print("📋 Basado en la documentación oficial")
    print("🎯 Puerto 5003 (Backend) + Puerto 8000 (Frontend)")
    print("=" * 50)
    
    # Limpiar procesos
    kill_all_processes()
    
    # Iniciar backend
    if not start_backend():
        print("❌ No se pudo iniciar el backend")
        return False
    
    # Iniciar frontend
    if not start_frontend():
        print("❌ No se pudo iniciar el frontend")
        return False
    
    print("\n🎉 SISTEMA RESTAURADO EXITOSAMENTE")
    print("=" * 50)
    print("📱 Frontend: http://localhost:8000")
    print("🔧 Backend: http://localhost:5003")
    print("📡 WebSocket: ws://localhost:5003")
    print("\n✅ Tu bot web está funcionando correctamente")
    print("🚀 Puedes acceder a la interfaz ahora")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Restauración interrumpida")
    except Exception as e:
        print(f"\n❌ Error durante la restauración: {e}")

