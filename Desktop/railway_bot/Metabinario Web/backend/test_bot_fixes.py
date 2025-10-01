#!/usr/bin/env python3
"""
PROBAR CORRECCIONES DEL BOT DEL SEGUIDOR
"""

import requests
import json
import time

WEB_BASE_URL = "http://localhost:5003"

def test_bot_fixes():
    """Probar las correcciones del bot del seguidor"""
    print("🧪 PROBANDO CORRECCIONES DEL BOT DEL SEGUIDOR")
    print("=" * 60)
    
    # 1. Login como seguidor
    print("1️⃣ Conectando como seguidor...")
    session = requests.Session()
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
    
    # 2. Verificar estado inicial
    print("2️⃣ Verificando estado inicial...")
    status1 = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    if status1.status_code == 200:
        data1 = status1.json()
        print(f"📊 Estado inicial: {data1}")
        initial_status = data1.get('bot_status', False)
    else:
        print(f"❌ Error obteniendo estado: {status1.status_code}")
        return False
    
    # 3. Encender bot
    print("3️⃣ Encendiendo bot...")
    start = session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if start.status_code == 200:
        print("✅ Bot encendido")
    else:
        print(f"❌ Error encendiendo bot: {start.status_code}")
        return False
    
    # 4. Verificar estado después de encender
    print("4️⃣ Verificando estado después de encender...")
    time.sleep(2)
    status2 = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    if status2.status_code == 200:
        data2 = status2.json()
        print(f"📊 Estado después de encender: {data2}")
        after_start_status = data2.get('bot_status', False)
    else:
        print(f"❌ Error obteniendo estado: {status2.status_code}")
        return False
    
    # 5. Activar auto copy (esto antes causaba problemas)
    print("5️⃣ Activando auto copy (esto antes causaba problemas)...")
    trader_session = requests.Session()
    trader_login = trader_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "binariosector91@outlook.com",
        "password": "12345678",
        "role": "trader",
        "balance_mode": "PRACTICE"
    })
    
    if trader_login.status_code == 200:
        auto_copy = trader_session.post(f"{WEB_BASE_URL}/api/trader/start-auto-copy")
        if auto_copy.status_code == 200:
            print("✅ Auto copy activado")
        else:
            print(f"❌ Error activando auto copy: {auto_copy.status_code}")
    else:
        print(f"❌ Error login trader: {trader_login.status_code}")
    
    # 6. Verificar estado después de auto copy
    print("6️⃣ Verificando estado después de auto copy...")
    time.sleep(3)
    status3 = session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
    if status3.status_code == 200:
        data3 = status3.json()
        print(f"📊 Estado después de auto copy: {data3}")
        after_auto_copy_status = data3.get('bot_status', False)
    else:
        print(f"❌ Error obteniendo estado: {status3.status_code}")
        return False
    
    # 7. Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBA:")
    print(f"   Estado inicial: {'ENCENDIDO' if initial_status else 'APAGADO'}")
    print(f"   Después de encender: {'ENCENDIDO' if after_start_status else 'APAGADO'}")
    print(f"   Después de auto copy: {'ENCENDIDO' if after_auto_copy_status else 'APAGADO'}")
    
    if after_auto_copy_status:
        print("🎉 ¡CORRECCIÓN EXITOSA! El bot mantiene su estado después de auto copy")
        return True
    else:
        print("❌ El bot sigue perdiendo su estado - necesita más correcciones")
        return False

if __name__ == "__main__":
    test_bot_fixes()
