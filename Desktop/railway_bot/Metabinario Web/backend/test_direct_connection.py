#!/usr/bin/env python3
"""
Script de prueba directa para verificar la conexión con ExNova
"""

import sys
import os
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

from exnovaapi.stable_api import Exnova
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_direct_connection():
    """Probar conexión directa con ExNova"""
    logger.info("🧪 PROBANDO CONEXIÓN DIRECTA CON EXNOVA")
    logger.info("=" * 50)
    
    # Credenciales de prueba
    email = "binariosector91@outlook.com"
    password = "Binaryoptions91"
    balance_mode = "PRACTICE"
    
    try:
        logger.info(f"1️⃣ Conectando con {email}...")
        connection = Exnova(email, password)
        
        logger.info("2️⃣ Iniciando conexión...")
        connection.connect()
        
        if hasattr(connection, 'api') and connection.api:
            logger.info("✅ Conexión exitosa!")
            
            logger.info("3️⃣ Cambiando balance mode...")
            connection.change_balance(balance_mode)
            
            logger.info("4️⃣ Verificando socket de operaciones...")
            if hasattr(connection.api, 'socket_option_opened'):
                operations = connection.api.socket_option_opened
                logger.info(f"✅ Socket de operaciones disponible: {len(operations)} operaciones")
            else:
                logger.warning("⚠️ Socket de operaciones no disponible")
            
            logger.info("5️⃣ Probando operación...")
            success, result = connection.buy(10, "EURUSD-OTC", "CALL", 2)
            
            if success:
                logger.info(f"✅ Operación exitosa: {result}")
            else:
                logger.error(f"❌ Error en operación: {result}")
            
            logger.info("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
            return True
            
        else:
            logger.error("❌ Error: No se pudo obtener la API")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en conexión: {e}")
        return False

if __name__ == "__main__":
    test_direct_connection()





