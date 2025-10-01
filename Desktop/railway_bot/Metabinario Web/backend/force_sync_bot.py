#!/usr/bin/env python3
"""
FORZAR SINCRONIZACIÓN DEL BOT DEL SEGUIDOR
"""

import requests
import json
import time

WEB_BASE_URL = "http://localhost:5003"

def force_sync_bot():
    """Forzar sincronización del bot del seguidor"""
    print("🔄 FORZANDO SINCRONIZACIÓN DEL BOT")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. Login como seguidor
    print("1️⃣ Conectando como seguidor...")
    login = session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "clickrealbinarias@outlook.com",
        "password": "Galileatrade27$",
        "role": "follower",
        "balance_mode": "PRACTICE",
        "amount": 15.0
    })
    
    if login.status_code != 200:
        print(f"❌ Error en login: {login.status_code}")
        return False
    
    print("✅ Seguidor conectado")
    
    # 2. Apagar bot
    print("2️⃣ Apagando bot...")
    stop_bot = session.post(f"{WEB_BASE_URL}/api/follower/stop-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if stop_bot.status_code == 200:
        print("✅ Bot apagado")
    else:
        print(f"⚠️ Error apagando bot: {stop_bot.status_code}")
    
    # 3. Esperar un momento
    print("3️⃣ Esperando...")
    time.sleep(3)
    
    # 4. Encender bot
    print("4️⃣ Encendiendo bot...")
    start_bot = session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if start_bot.status_code == 200:
        print("✅ Bot encendido")
    else:
        print(f"❌ Error encendiendo bot: {start_bot.status_code}")
        return False
    
    # 5. Verificar estado final
    print("5️⃣ Verificando estado final...")
    time.sleep(3)
    
    final_status = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    if final_status.status_code == 200:
        final_data = final_status.json()
        final_bot_status = final_data.get('bot_status', False)
        print(f"📊 Estado final: {'ENCENDIDO' if final_bot_status else 'APAGADO'}")
        
        if final_bot_status:
            print("🎉 ¡BOT SINCRONIZADO CORRECTAMENTE!")
            return True
        else:
            print("❌ El bot sigue apagado")
            return False
    else:
        print(f"❌ Error verificando estado: {final_status.status_code}")
        return False

if __name__ == "__main__":
    force_sync_bot()





