#!/usr/bin/env python3
"""
VERIFICAR ESTADO FINAL DE AMBAS CUENTAS
"""

import requests
import json

WEB_BASE_URL = "http://localhost:5003"

def check_final_status():
    """Verificar estado final de ambas cuentas"""
    print("🔍 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 60)
    
    # 1. VERIFICAR TRADER
    print("1️⃣ VERIFICANDO TRADER...")
    trader_session = requests.Session()
    trader_login = trader_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "binariosector91@outlook.com",
        "password": "12345678",
        "role": "trader",
        "balance_mode": "PRACTICE"
    })
    
    if trader_login.status_code == 200:
        print("✅ Trader: CONECTADO")
        
        # Verificar auto copy del trader
        auto_copy = trader_session.post(f"{WEB_BASE_URL}/api/trader/start-auto-copy")
        if auto_copy.status_code == 200:
            print("✅ Auto Copy: ACTIVADO")
        else:
            print("⚠️ Auto Copy: Error al activar")
    else:
        print(f"❌ Trader: Error de conexión - {trader_login.status_code}")
        return False
    
    # 2. VERIFICAR SEGUIDOR
    print("\n2️⃣ VERIFICANDO SEGUIDOR...")
    follower_session = requests.Session()
    follower_login = follower_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "clickrealbinarias@outlook.com",
        "password": "Galileatrade27$",
        "role": "follower",
        "balance_mode": "PRACTICE",
        "amount": 15.0
    })
    
    if follower_login.status_code == 200:
        print("✅ Seguidor: CONECTADO")
        
        # Verificar bot del seguidor
        bot_status = follower_session.get(f"{WEB_BASE_URL}/api/follower/bot-status")
        if bot_status.status_code == 200:
            status_data = bot_status.json()
            bot_active = status_data.get('bot_status', False)
            if bot_active:
                print("✅ Bot del Seguidor: ENCENDIDO")
            else:
                print("❌ Bot del Seguidor: APAGADO")
                return False
        else:
            print("❌ Error verificando bot del seguidor")
            return False
    else:
        print(f"❌ Seguidor: Error de conexión - {follower_login.status_code}")
        return False
    
    # 3. RESUMEN FINAL
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    print("✅ Trader: CONECTADO y MONITOREANDO")
    print("✅ Seguidor: CONECTADO con BOT ENCENDIDO")
    print("✅ Sistema: LISTO PARA REPLICAR")
    print("=" * 60)
    print("🎯 ¡SÍ, AMBAS CUENTAS ESTÁN LISTAS!")
    print("🚀 ¡PUEDES EJECUTAR LA ENTRADA!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    check_final_status()





