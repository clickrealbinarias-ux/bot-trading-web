#!/usr/bin/env python3
"""
DIAGNÓSTICO DE CONEXIÓN EXNOVA
Diagnostica problemas de conexión con ExNova
"""

import sys
import os
import time
import logging

# Agregar el directorio exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_exnova_connection():
    """Probar conexión directa con ExNova"""
    try:
        logger.info("🔍 Probando conexión directa con ExNova...")
        
        # Importar ExNovaAPI
        from exnovaapi.stable_api import ExnovaAPI
        
        # Crear instancia
        api = ExnovaAPI()
        
        # Probar login
        logger.info("🔐 Probando login...")
        result = api.login("binariosector91@outlook.com", "Galileatrade27$")
        
        if result:
            logger.info("✅ Login exitoso")
            
            # Probar obtener perfil
            logger.info("👤 Obteniendo perfil...")
            profile = api.get_profile()
            if profile:
                logger.info(f"✅ Perfil obtenido: {profile}")
            else:
                logger.warning("⚠️ No se pudo obtener perfil")
            
            # Probar cerrar sesión
            logger.info("🚪 Cerrando sesión...")
            api.logout()
            logger.info("✅ Sesión cerrada")
            
            return True
        else:
            logger.error("❌ Login falló")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en conexión ExNova: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_websocket_connection():
    """Probar conexión websocket"""
    try:
        logger.info("🔌 Probando conexión websocket...")
        
        from exnovaapi.ws.client import WebsocketClient
        import asyncio
        
        # Crear cliente websocket
        client = WebsocketClient()
        
        # Probar métodos
        logger.info("📋 Métodos disponibles en WebsocketClient:")
        methods = [m for m in dir(client) if not m.startswith('_')]
        for method in methods:
            logger.info(f"   - {method}")
        
        # Verificar firma de on_close
        import inspect
        sig = inspect.signature(client.on_close)
        logger.info(f"🔍 Firma de on_close: {sig}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en websocket: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_our_copytrading_api():
    """Probar OurCopyTradingAPI"""
    try:
        logger.info("🤖 Probando OurCopyTradingAPI...")
        
        # Importar desde el bot web
        sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend')
        from our_copytrading_api import OurCopyTradingAPI
        
        # Crear instancia
        api = OurCopyTradingAPI()
        logger.info("✅ OurCopyTradingAPI creada correctamente")
        
        # Probar agregar trader
        logger.info("👤 Probando agregar trader...")
        result = api.add_trader_account(
            "binariosector91@outlook.com",
            "Galileatrade27$",
            "PRACTICE"
        )
        
        if result:
            logger.info("✅ Trader agregado correctamente")
            
            # Obtener estado
            status = api.get_status()
            logger.info(f"📊 Estado: {status}")
            
            # Limpiar
            api.cleanup()
            logger.info("🧹 Limpieza completada")
            
            return True
        else:
            logger.error("❌ No se pudo agregar trader")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en OurCopyTradingAPI: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal de diagnóstico"""
    logger.info("🔍 INICIANDO DIAGNÓSTICO DE CONEXIÓN EXNOVA")
    logger.info("=" * 60)
    
    # 1. Probar conexión directa
    logger.info("1️⃣ Probando conexión directa con ExNova...")
    direct_success = test_exnova_connection()
    
    # 2. Probar websocket
    logger.info("2️⃣ Probando conexión websocket...")
    ws_success = test_websocket_connection()
    
    # 3. Probar OurCopyTradingAPI
    logger.info("3️⃣ Probando OurCopyTradingAPI...")
    api_success = test_our_copytrading_api()
    
    # Resumen
    logger.info("=" * 60)
    logger.info("📊 RESUMEN DEL DIAGNÓSTICO")
    logger.info(f"🔗 Conexión directa ExNova: {'✅' if direct_success else '❌'}")
    logger.info(f"🔌 Conexión websocket: {'✅' if ws_success else '❌'}")
    logger.info(f"🤖 OurCopyTradingAPI: {'✅' if api_success else '❌'}")
    
    if all([direct_success, ws_success, api_success]):
        logger.info("🎉 TODOS LOS TESTS PASARON")
    else:
        logger.error("💥 ALGUNOS TESTS FALLARON")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

