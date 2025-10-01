#!/usr/bin/env python3
"""
Script de prueba para verificar que la replicación funciona correctamente
"""

import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración
WEB_BOT_URL = "http://127.0.0.1:5003/api"
TRADER_EMAIL = "binariosector91@outlook.com"
TRADER_PASSWORD = "Binaryoptions91"
FOLLOWER_EMAIL = "clickrealbinarias@outlook.com"
FOLLOWER_PASSWORD = "Binaryoptions91"
BALANCE_MODE = "PRACTICE"

def test_web_bot_replication():
    """Probar la replicación del web bot"""
    logger.info("🧪 INICIANDO PRUEBA DE REPLICACIÓN")
    logger.info("=" * 50)
    
    # 1. Login como trader
    logger.info("1️⃣ Iniciando sesión como trader...")
    trader_login = login_user(TRADER_EMAIL, TRADER_PASSWORD, "trader", BALANCE_MODE)
    if not trader_login:
        logger.error("❌ Error en login del trader")
        return False
    
    # 2. Login como seguidor
    logger.info("2️⃣ Iniciando sesión como seguidor...")
    follower_login = login_user(FOLLOWER_EMAIL, FOLLOWER_PASSWORD, "follower", BALANCE_MODE)
    if not follower_login:
        logger.error("❌ Error en login del seguidor")
        return False
    
    # 3. Encender bot del seguidor
    logger.info("3️⃣ Encendiendo bot del seguidor...")
    start_bot = start_follower_bot(FOLLOWER_EMAIL)
    if not start_bot:
        logger.error("❌ Error encendiendo bot del seguidor")
        return False
    
    # 4. Verificar estado del bot
    logger.info("4️⃣ Verificando estado del bot...")
    bot_status = get_follower_bot_status()
    if bot_status:
        logger.info(f"✅ Estado del bot: {'ENCENDIDO' if bot_status.get('bot_status') else 'APAGADO'}")
    else:
        logger.warning("⚠️ No se pudo obtener el estado del bot")
    
    # 5. Activar auto-copy
    logger.info("5️⃣ Activando auto-copy...")
    auto_copy = activate_auto_copy()
    if not auto_copy:
        logger.error("❌ Error activando auto-copy")
        return False
    
    # 6. Verificar estado del sistema
    logger.info("6️⃣ Verificando estado del sistema...")
    system_status = get_system_status()
    if system_status:
        logger.info(f"✅ Auto-copy activo: {system_status.get('auto_copy_active', False)}")
        logger.info(f"✅ Seguidores: {system_status.get('followers_count', 0)}")
    
    logger.info("🎉 CONFIGURACIÓN COMPLETADA")
    logger.info("=" * 50)
    logger.info("📋 INSTRUCCIONES PARA PROBAR:")
    logger.info("1. Abre el navegador en http://127.0.0.1:5003")
    logger.info("2. Inicia sesión con las mismas credenciales")
    logger.info("3. Verifica que el bot del seguidor esté ENCENDIDO")
    logger.info("4. Verifica que el auto-copy esté ACTIVO")
    logger.info("5. Realiza una operación desde el bot original de Telegram")
    logger.info("6. Verifica que se replica en la cuenta seguidor")
    logger.info("=" * 50)
    
    return True

def login_user(email, password, role, balance_mode):
    """Iniciar sesión de usuario"""
    try:
        response = requests.post(f"{WEB_BOT_URL}/login", json={
            "email": email,
            "password": password,
            "role": role,
            "balance_mode": balance_mode,
            "amount": 10.0
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info(f"✅ Login exitoso: {email} ({role})")
                return data
            else:
                logger.error(f"❌ Error en login: {data.get('error')}")
                return None
        else:
            logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error en login: {e}")
        return None

def start_follower_bot(email):
    """Encender bot del seguidor"""
    try:
        response = requests.post(f"{WEB_BOT_URL}/follower/start-bot", json={
            "email": email
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info(f"✅ Bot del seguidor encendido: {email}")
                return True
            else:
                logger.error(f"❌ Error encendiendo bot: {data.get('error')}")
                return False
        else:
            logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error encendiendo bot: {e}")
        return False

def get_follower_bot_status():
    """Obtener estado del bot del seguidor"""
    try:
        response = requests.get(f"{WEB_BOT_URL}/follower/bot-status")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data
            else:
                logger.error(f"❌ Error obteniendo estado: {data.get('error')}")
                return None
        else:
            logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado: {e}")
        return None

def activate_auto_copy():
    """Activar auto-copy"""
    try:
        response = requests.post(f"{WEB_BOT_URL}/trader/start-auto-copy")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                logger.info("✅ Auto-copy activado")
                return True
            else:
                logger.error(f"❌ Error activando auto-copy: {data.get('error')}")
                return False
        else:
            logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error activando auto-copy: {e}")
        return False

def get_system_status():
    """Obtener estado del sistema"""
    try:
        response = requests.get(f"{WEB_BOT_URL}/status")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data
            else:
                logger.error(f"❌ Error obteniendo estado: {data.get('error')}")
                return None
        else:
            logger.error(f"❌ Error HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado: {e}")
        return None

if __name__ == "__main__":
    test_web_bot_replication()





