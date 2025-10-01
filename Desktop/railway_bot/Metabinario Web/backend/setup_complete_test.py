#!/usr/bin/env python3
"""
SCRIPT COMPLETO PARA CONFIGURAR Y PROBAR EL BOT WEB
"""

import sys
import os
import time
import requests
import json
import threading

# Configuración
WEB_BASE_URL = "http://localhost:5003"

def setup_complete_test():
    """Configurar y probar el bot web completo"""
    print("🚀 CONFIGURACIÓN COMPLETA DEL BOT WEB")
    print("=" * 60)
    
    # Crear sesiones separadas para trader y follower
    trader_session = requests.Session()
    follower_session = requests.Session()
    
    # 1. LOGIN TRADER
    print("1️⃣ INICIANDO SESIÓN COMO TRADER...")
    trader_login = trader_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "binariosector91@outlook.com",
        "password": "12345678",
        "role": "trader",
        "balance_mode": "PRACTICE"
    })
    
    if trader_login.status_code != 200:
        print(f"❌ Error en login trader: {trader_login.status_code} - {trader_login.text}")
        return False
    
    print("✅ Trader conectado exitosamente")
    
    # 2. LOGIN FOLLOWER
    print("2️⃣ INICIANDO SESIÓN COMO SEGUIDOR...")
    follower_login = follower_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "clickrealbinarias@outlook.com",
        "password": "Galileatrade27$",
        "role": "follower",
        "balance_mode": "PRACTICE",
        "amount": 15.0
    })
    
    if follower_login.status_code != 200:
        print(f"❌ Error en login follower: {follower_login.status_code} - {follower_login.text}")
        return False
    
    print("✅ Seguidor conectado exitosamente")
    
    # 3. VERIFICAR ESTADO DEL BOT DEL SEGUIDOR
    print("3️⃣ VERIFICANDO ESTADO DEL BOT DEL SEGUIDOR...")
    bot_status = follower_session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if bot_status.status_code == 200:
        status_data = bot_status.json()
        print(f"📊 Estado actual del bot: {status_data}")
        current_status = status_data.get('bot_status', False)
        print(f"🤖 Bot está: {'ENCENDIDO' if current_status else 'APAGADO'}")
    else:
        print(f"❌ Error obteniendo estado: {bot_status.status_code}")
        return False
    
    # 4. ENCENDER BOT DEL SEGUIDOR SI ESTÁ APAGADO
    if not current_status:
        print("4️⃣ ENCENDIENDO BOT DEL SEGUIDOR...")
        start_bot = follower_session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
            "email": "clickrealbinarias@outlook.com"
        })
        
        if start_bot.status_code == 200:
            print("✅ Bot del seguidor encendido exitosamente")
        else:
            print(f"❌ Error encendiendo bot: {start_bot.status_code} - {start_bot.text}")
            return False
    else:
        print("✅ Bot del seguidor ya estaba encendido")
    
    # 5. VERIFICAR ESTADO FINAL
    print("5️⃣ VERIFICANDO ESTADO FINAL...")
    time.sleep(2)
    final_status = follower_session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if final_status.status_code == 200:
        final_data = final_status.json()
        print(f"📊 Estado final del bot: {final_data}")
        final_bot_status = final_data.get('bot_status', False)
        print(f"🤖 Bot final: {'ENCENDIDO' if final_bot_status else 'APAGADO'}")
        
        if final_bot_status:
            print("🎉 ¡CONFIGURACIÓN COMPLETA! El bot está listo para replicar")
            return True
        else:
            print("❌ El bot sigue apagado después de intentar encenderlo")
            return False
    else:
        print(f"❌ Error verificando estado final: {final_status.status_code}")
        return False

def monitor_operations():
    """Monitorear operaciones en tiempo real"""
    print("\n🔍 INICIANDO MONITOR DE OPERACIONES...")
    print("=" * 60)
    
    # Leer logs en tiempo real
    import subprocess
    try:
        process = subprocess.Popen(
            ['tail', '-f', '/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend/copytrading_web.log'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("📡 Monitoreando logs en tiempo real...")
        print("💡 Presiona Ctrl+C para detener el monitoreo")
        print("-" * 60)
        
        for line in iter(process.stdout.readline, ''):
            if 'NUEVA OPERACIÓN' in line or 'Replicando' in line or 'ENCENDIDO' in line or 'APAGADO' in line:
                print(f"🔔 {line.strip()}")
                
    except KeyboardInterrupt:
        print("\n🛑 Monitoreo detenido")
        process.terminate()
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")

def main():
    """Función principal"""
    print("🎯 CONFIGURACIÓN AUTOMÁTICA DEL BOT WEB")
    print("=" * 60)
    
    # Configurar el sistema
    success = setup_complete_test()
    
    if success:
        print("\n✅ CONFIGURACIÓN EXITOSA")
        print("🎯 El bot está listo para replicar operaciones")
        print("📊 Ahora puedes tomar operaciones como trader")
        print("🔄 El seguidor replicará automáticamente")
        
        # Preguntar si quiere monitorear
        response = input("\n¿Quieres monitorear las operaciones en tiempo real? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            monitor_operations()
    else:
        print("\n❌ CONFIGURACIÓN FALLIDA")
        print("🔧 Revisa los logs para más detalles")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

