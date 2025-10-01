#!/usr/bin/env python3
"""
PROBAR OPERACIÓN MANUAL PARA VERIFICAR REPLICACIÓN
"""

import requests
import json
import time

WEB_BASE_URL = "http://localhost:5003"

def test_manual_operation():
    """Probar operación manual"""
    print("🧪 PROBANDO OPERACIÓN MANUAL")
    print("=" * 50)
    
    # 1. Login como trader
    print("1️⃣ Conectando como trader...")
    trader_session = requests.Session()
    trader_login = trader_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "binariosector91@outlook.com",
        "password": "12345678",
        "role": "trader",
        "balance_mode": "PRACTICE"
    })
    
    if trader_login.status_code != 200:
        print(f"❌ Error en login trader: {trader_login.status_code}")
        return False
    
    print("✅ Trader conectado")
    
    # 2. Login como seguidor
    print("2️⃣ Conectando como seguidor...")
    follower_session = requests.Session()
    follower_login = follower_session.post(f"{WEB_BASE_URL}/api/login", json={
        "email": "clickrealbinarias@outlook.com",
        "password": "Galileatrade27$",
        "role": "follower",
        "balance_mode": "PRACTICE",
        "amount": 15.0
    })
    
    if follower_login.status_code != 200:
        print(f"❌ Error en login follower: {follower_login.status_code}")
        return False
    
    print("✅ Seguidor conectado")
    
    # 3. Asegurar que el bot del seguidor esté encendido
    print("3️⃣ Asegurando que el bot esté encendido...")
    start_bot = follower_session.post(f"{WEB_BASE_URL}/api/follower/start-bot", json={
        "email": "clickrealbinarias@outlook.com"
    })
    
    if start_bot.status_code == 200:
        print("✅ Bot del seguidor encendido")
    else:
        print(f"❌ Error encendiendo bot: {start_bot.status_code}")
        return False
    
    # 4. Esperar un momento
    print("4️⃣ Esperando 3 segundos...")
    time.sleep(3)
    
    # 5. Ejecutar operación manual
    print("5️⃣ Ejecutando operación manual...")
    operation = trader_session.post(f"{WEB_BASE_URL}/api/trader/execute-operation", json={
        "amount": 10.0,
        "active": "EURUSD-OTC",
        "direction": "CALL",
        "duration": 2
    })
    
    if operation.status_code == 200:
        operation_data = operation.json()
        print(f"✅ Operación ejecutada: {operation_data}")
    else:
        print(f"❌ Error ejecutando operación: {operation.status_code} - {operation.text}")
        return False
    
    # 6. Esperar y verificar logs
    print("6️⃣ Esperando 10 segundos para verificar replicación...")
    time.sleep(10)
    
    print("✅ Prueba completada. Revisa los logs para ver si se replicó.")
    return True

if __name__ == "__main__":
    test_manual_operation()





