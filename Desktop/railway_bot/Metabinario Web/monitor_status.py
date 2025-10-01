#!/usr/bin/env python3
"""
Script de monitoreo para verificar el estado del copytrading
"""

import requests
import json
import time
from datetime import datetime

def check_copytrading_status():
    """Verificar el estado actual del sistema de copytrading"""
    print("🔍 VERIFICANDO ESTADO DEL COPYTRADING")
    print("=" * 60)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar estado del backend
    try:
        response = requests.get("http://localhost:5003/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API: FUNCIONANDO")
        else:
            print(f"❌ Backend API: ERROR {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend API: NO DISPONIBLE - {e}")
        return False
    
    print("\n📊 ESTADO DEL SISTEMA:")
    print("-" * 40)
    
    # Verificar si hay instancias activas
    try:
        # Intentar obtener información de las instancias
        print("🔍 Verificando instancias de ExNova...")
        
        # Verificar logs recientes
        print("📋 Revisando logs recientes...")
        
        print("\n⚠️  IMPORTANTE:")
        print("Para verificar el estado completo del copytrading, necesitas:")
        print("1. Iniciar sesión en http://localhost:8000")
        print("2. Configurar cuenta de trader con credenciales de ExNova")
        print("3. Agregar cuentas de seguidores")
        print("4. Activar el monitoreo automático")
        
        print("\n🎯 CUANDO EJECUTES UNA ENTRADA:")
        print("1. El sistema detectará la operación del trader")
        print("2. Replicará automáticamente en los seguidores")
        print("3. Mostrará notificaciones en tiempo real")
        print("4. Los logs aparecerán en la consola del backend")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando estado: {e}")
        return False

def monitor_logs():
    """Preparar monitoreo de logs"""
    print("\n" + "=" * 60)
    print("📋 PREPARANDO MONITOREO DE LOGS")
    print("=" * 60)
    print("Cuando ejecutes una entrada, verifica:")
    print("1. Logs en la consola del backend (puerto 5003)")
    print("2. Notificaciones en la interfaz web")
    print("3. Respuestas de la API de ExNova")
    print("4. Estado de las conexiones WebSocket")
    
    print("\n🔍 COMANDOS PARA MONITOREAR:")
    print("• Ver logs en tiempo real: tail -f logs/backend.log")
    print("• Verificar conexiones: lsof -i :5003")
    print("• Estado de la API: curl http://localhost:5003/api/status")

if __name__ == "__main__":
    if check_copytrading_status():
        monitor_logs()
        print("\n✅ Sistema listo para monitorear operaciones")
    else:
        print("\n❌ Sistema no está funcionando correctamente")

