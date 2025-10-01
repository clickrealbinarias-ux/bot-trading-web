#!/usr/bin/env python3
"""
SCRIPT DE PRUEBA PARA VERIFICAR EL BOT DEL SEGUIDOR
"""

import sys
import os
import time
import requests
import json

# Configuración
WEB_BASE_URL = "http://localhost:5003"

def test_follower_bot():
    """Probar el bot del seguidor"""
    print("🧪 INICIANDO PRUEBA DEL BOT DEL SEGUIDOR")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Login como seguidor
    print("1️⃣ Haciendo login como seguidor...")
    login_response = session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "clickrealbinarias@outlook.com",
        "password": "Galileatrade27$",
        "role": "follower",
        "balance_mode": "PRACTICE",
        "amount": 15.0
    })
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code} - {login_response.text}")
        return False
    
    print("✅ Login exitoso")
    
    # 2. Obtener estado del bot
    print("2️⃣ Obteniendo estado del bot...")
    status_response = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"📊 Estado del bot: {status_data}")
        bot_status = status_data.get('bot_status', False)
        print(f"🤖 Bot está: {'ENCENDIDO' if bot_status else 'APAGADO'}")
    else:
        print(f"❌ Error obteniendo estado: {status_response.status_code}")
        return False
    
    # 3. Encender el bot
    print("3️⃣ Encendiendo el bot...")
    start_response = session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if start_response.status_code == 200:
        start_data = start_response.json()
        print(f"✅ Respuesta de encender: {start_data}")
    else:
        print(f"❌ Error encendiendo bot: {start_response.status_code} - {start_response.text}")
        return False
    
    # 4. Verificar estado después de encender
    print("4️⃣ Verificando estado después de encender...")
    time.sleep(2)
    status_response = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"📊 Estado del bot: {status_data}")
        bot_status = status_data.get('bot_status', False)
        print(f"🤖 Bot está: {'ENCENDIDO' if bot_status else 'APAGADO'}")
        
        if bot_status:
            print("🎉 ¡BOT ENCENDIDO EXITOSAMENTE!")
            return True
        else:
            print("❌ El bot sigue apagado")
            return False
    else:
        print(f"❌ Error verificando estado: {status_response.status_code}")
        return False

def main():
    """Función principal"""
    success = test_follower_bot()
    
    if success:
        print("\n🎉 PRUEBA EXITOSA - El bot del seguidor funciona correctamente")
    else:
        print("\n💥 PRUEBA FALLIDA - Hay problemas con el bot del seguidor")
    
    print("=" * 60)

if __name__ == "__main__":
    main()

