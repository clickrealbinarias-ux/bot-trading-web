#!/usr/bin/env python3
"""
VERIFICAR ESTADO REAL DEL SISTEMA
"""

import requests
import json

WEB_BASE_URL = "http://localhost:5003"

def check_real_status():
    """Verificar estado real del sistema"""
    print("🔍 VERIFICANDO ESTADO REAL DEL SISTEMA")
    print("=" * 60)
    
    # 1. Verificar trader
    print("1️⃣ VERIFICANDO TRADER...")
    trader_session = requests.Session()
    trader_login = trader_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "binariosector91@outlook.com",
        "password": "12345678",
        "role": "trader",
        "balance_mode": "PRACTICE"
    })
    
    if trader_login.status_code == 200:
        print("✅ Trader conectado")
    else:
        print(f"❌ Error trader: {trader_login.status_code}")
        return False
    
    # 2. Verificar seguidor
    print("2️⃣ VERIFICANDO SEGUIDOR...")
    follower_session = requests.Session()
    follower_login = follower_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "clickrealbinarias@outlook.com",
        "password": "Galileatrade27$",
        "role": "follower",
        "balance_mode": "PRACTICE",
        "amount": 15.0
    })
    
    if follower_login.status_code == 200:
        print("✅ Seguidor conectado")
    else:
        print(f"❌ Error seguidor: {follower_login.status_code}")
        return False
    
    # 3. Verificar estado del bot del seguidor
    print("3️⃣ VERIFICANDO ESTADO DEL BOT...")
    bot_status = follower_session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    
    if bot_status.status_code == 200:
        status_data = bot_status.json()
        print(f"📊 Estado del bot: {status_data}")
        current_status = status_data.get('bot_status', False)
        print(f"🤖 Bot está: {'ENCENDIDO' if current_status else 'APAGADO'}")
        
        if not current_status:
            print("4️⃣ ENCENDIENDO BOT...")
            start_bot = follower_session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
                "email": "clickrealbinarias@outlook.com"
            })
            
            if start_bot.status_code == 200:
                print("✅ Bot encendido")
                
                # Verificar estado final
                import time
                time.sleep(2)
                final_status = follower_session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
                if final_status.status_code == 200:
                    final_data = final_status.json()
                    final_bot_status = final_data.get('bot_status', False)
                    print(f"📊 Estado final: {'ENCENDIDO' if final_bot_status else 'APAGADO'}")
                    
                    if final_bot_status:
                        print("🎉 ¡BOT ACTIVADO CORRECTAMENTE!")
                        return True
                    else:
                        print("❌ El bot sigue apagado")
                        return False
            else:
                print(f"❌ Error encendiendo bot: {start_bot.status_code} - {start_bot.text}")
                return False
        else:
            print("✅ Bot ya estaba encendido")
            return True
    else:
        print(f"❌ Error obteniendo estado: {bot_status.status_code}")
        return False

if __name__ == "__main__":
    check_real_status()





