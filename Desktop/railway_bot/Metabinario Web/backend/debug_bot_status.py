#!/usr/bin/env python3
"""
DEBUG COMPLETO DEL ESTADO DEL BOT
"""

import requests
import json
import time

WEB_BASE_URL = "http://localhost:5003"

def debug_bot_status():
    """Debug completo del estado del bot"""
    print("🔍 DEBUG COMPLETO DEL ESTADO DEL BOT")
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
    
    # 2. Verificar estado actual
    print("2️⃣ Verificando estado actual...")
    status = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if status.status_code == 200:
        status_data = status.json()
        print(f"📊 Estado del bot: {status_data}")
        current_status = status_data.get('bot_status', False)
        print(f"🤖 Bot está: {'ENCENDIDO' if current_status else 'APAGADO'}")
    else:
        print(f"❌ Error obteniendo estado: {status.status_code}")
        return False
    
    # 3. Forzar apagado
    print("3️⃣ Forzando apagado...")
    stop_bot = session.post(f"{WEB_BASE_URL}/api/follower/stop-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if stop_bot.status_code == 200:
        print("✅ Bot apagado")
    else:
        print(f"⚠️ Error apagando bot: {stop_bot.status_code}")
    
    # 4. Esperar
    print("4️⃣ Esperando 3 segundos...")
    time.sleep(3)
    
    # 5. Verificar estado después de apagar
    print("5️⃣ Verificando estado después de apagar...")
    status_after_stop = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if status_after_stop.status_code == 200:
        status_data = status_after_stop.json()
        print(f"📊 Estado después de apagar: {status_data}")
        status_after = status_data.get('bot_status', False)
        print(f"🤖 Bot después de apagar: {'ENCENDIDO' if status_after else 'APAGADO'}")
    else:
        print(f"❌ Error verificando estado: {status_after_stop.status_code}")
    
    # 6. Forzar encendido
    print("6️⃣ Forzando encendido...")
    start_bot = session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if start_bot.status_code == 200:
        print("✅ Bot encendido")
    else:
        print(f"❌ Error encendiendo bot: {start_bot.status_code}")
        return False
    
    # 7. Esperar
    print("7️⃣ Esperando 5 segundos...")
    time.sleep(5)
    
    # 8. Verificar estado final
    print("8️⃣ Verificando estado final...")
    final_status = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if final_status.status_code == 200:
        final_data = final_status.json()
        print(f"📊 Estado final: {final_data}")
        final_bot_status = final_data.get('bot_status', False)
        print(f"🤖 Bot final: {'ENCENDIDO' if final_bot_status else 'APAGADO'}")
        
        if final_bot_status:
            print("🎉 ¡BOT ENCENDIDO CORRECTAMENTE!")
            return True
        else:
            print("❌ El bot sigue apagado después de encenderlo")
            return False
    else:
        print(f"❌ Error verificando estado final: {final_status.status_code}")
        return False

if __name__ == "__main__":
    debug_bot_status()





