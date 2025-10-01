#!/usr/bin/env python3
"""
MONITOR DE COMPARACIÓN BOT WEB VS BOT ORIGINAL
Verifica que el bot web esté haciendo exactamente lo mismo que el bot original
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
import threading
import requests
from typing import Dict, List, Any

# Agregar el directorio exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

# Importar nuestras APIs
from our_copytrading_api import OurCopyTradingAPI as OriginalAPI
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend')
from our_copytrading_api import OurCopyTradingAPI as WebAPI

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor_comparison.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BotComparisonMonitor:
    """Monitor que compara el bot web con el bot original"""
    
    def __init__(self):
        self.original_api = OriginalAPI()
        self.web_api = WebAPI()
        self.monitoring = False
        self.comparison_results = []
        
        # URLs del bot web
        self.web_base_url = "http://localhost:5003"
        
        logger.info("🔍 Monitor de comparación inicializado")
    
    def start_monitoring(self):
        """Iniciar monitoreo en paralelo"""
        self.monitoring = True
        logger.info("🚀 Iniciando monitoreo de comparación...")
        
        # Crear threads para diferentes verificaciones
        threads = [
            threading.Thread(target=self._monitor_api_structure, daemon=True),
            threading.Thread(target=self._monitor_instances, daemon=True),
            threading.Thread(target=self._monitor_auto_copy_status, daemon=True),
            threading.Thread(target=self._monitor_follower_bots, daemon=True),
            threading.Thread(target=self._monitor_operations_detection, daemon=True),
            threading.Thread(target=self._monitor_replication_logic, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        logger.info("✅ Todos los monitores iniciados")
        
        # Mantener el monitor activo
        try:
            while self.monitoring:
                time.sleep(10)
                self._log_summary()
        except KeyboardInterrupt:
            logger.info("🛑 Monitor detenido por usuario")
            self.monitoring = False
    
    def _monitor_api_structure(self):
        """Verificar que la estructura de la API sea idéntica"""
        while self.monitoring:
            try:
                # Verificar métodos principales
                original_methods = [method for method in dir(self.original_api) if not method.startswith('_')]
                web_methods = [method for method in dir(self.web_api) if not method.startswith('_')]
                
                missing_methods = set(original_methods) - set(web_methods)
                extra_methods = set(web_methods) - set(original_methods)
                
                if missing_methods or extra_methods:
                    logger.warning(f"⚠️ Diferencias en métodos de API:")
                    if missing_methods:
                        logger.warning(f"   Faltan en web: {missing_methods}")
                    if extra_methods:
                        logger.warning(f"   Extra en web: {extra_methods}")
                else:
                    logger.info("✅ Estructura de API idéntica")
                
                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ Error verificando estructura API: {e}")
                time.sleep(30)
    
    def _monitor_instances(self):
        """Verificar instancias de trader y seguidores"""
        while self.monitoring:
            try:
                # Verificar estado de instancias
                original_status = self.original_api.get_status()
                web_status = self.web_api.get_status()
                
                # Comparar trader
                original_trader = original_status.get('trader', {})
                web_trader = web_status.get('trader', {})
                
                if original_trader.get('connected') != web_trader.get('connected'):
                    logger.warning(f"⚠️ Estado de trader diferente: Original={original_trader.get('connected')}, Web={web_trader.get('connected')}")
                
                # Comparar seguidores
                original_followers = len(original_status.get('followers', []))
                web_followers = len(web_status.get('followers', []))
                
                if original_followers != web_followers:
                    logger.warning(f"⚠️ Número de seguidores diferente: Original={original_followers}, Web={web_followers}")
                
                logger.info(f"📊 Estado - Trader: {web_trader.get('connected', False)}, Seguidores: {web_followers}")
                
                time.sleep(15)
            except Exception as e:
                logger.error(f"❌ Error verificando instancias: {e}")
                time.sleep(15)
    
    def _monitor_auto_copy_status(self):
        """Verificar estado del copytrading automático"""
        while self.monitoring:
            try:
                # Verificar estado del auto copy
                original_auto_copy = self.original_api.is_auto_copy_active()
                web_auto_copy = self.web_api.is_auto_copy_active()
                
                if original_auto_copy != web_auto_copy:
                    logger.warning(f"⚠️ Estado de auto copy diferente: Original={original_auto_copy}, Web={web_auto_copy}")
                else:
                    logger.info(f"🤖 Auto copy activo: {web_auto_copy}")
                
                # Verificar variables internas
                original_active = getattr(self.original_api, 'auto_copy_active', False)
                web_active = getattr(self.web_api, 'auto_copy_active', False)
                
                if original_active != web_active:
                    logger.warning(f"⚠️ Variable auto_copy_active diferente: Original={original_active}, Web={web_active}")
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"❌ Error verificando auto copy: {e}")
                time.sleep(10)
    
    def _monitor_follower_bots(self):
        """Verificar estado de los bots de seguidores"""
        while self.monitoring:
            try:
                # Verificar estado de bots de seguidores
                web_status = self.web_api.get_status()
                followers = web_status.get('followers', [])
                
                for follower in followers:
                    email = follower.get('email', 'unknown')
                    bot_status = self.web_api.get_follower_bot_status(email)
                    connected = follower.get('connected', False)
                    
                    logger.info(f"👤 Seguidor {email}: Conectado={connected}, Bot={bot_status}")
                    
                    if connected and not bot_status:
                        logger.warning(f"⚠️ Seguidor {email} conectado pero bot APAGADO")
                
                time.sleep(20)
            except Exception as e:
                logger.error(f"❌ Error verificando bots de seguidores: {e}")
                time.sleep(20)
    
    def _monitor_operations_detection(self):
        """Verificar detección de operaciones"""
        while self.monitoring:
            try:
                # Verificar si hay instancia trader activa
                web_status = self.web_api.get_status()
                trader = web_status.get('trader', {})
                
                if trader.get('connected'):
                    # Verificar si el trader tiene result_queue
                    trader_instance = self.web_api.trader_instance
                    if trader_instance and hasattr(trader_instance, 'result_queue'):
                        queue_size = trader_instance.result_queue.qsize() if trader_instance.result_queue else 0
                        logger.info(f"📡 Trader result_queue size: {queue_size}")
                    else:
                        logger.warning("⚠️ Trader conectado pero sin result_queue")
                else:
                    logger.info("ℹ️ No hay trader conectado")
                
                time.sleep(5)
            except Exception as e:
                logger.error(f"❌ Error verificando detección de operaciones: {e}")
                time.sleep(5)
    
    def _monitor_replication_logic(self):
        """Verificar lógica de replicación"""
        while self.monitoring:
            try:
                # Verificar auto_copy_followers
                web_followers = getattr(self.web_api, 'auto_copy_followers', [])
                logger.info(f"🔄 Auto copy followers: {len(web_followers)}")
                
                for follower in web_followers:
                    email = getattr(follower, 'email', 'unknown')
                    bot_status = self.web_api.get_follower_bot_status(email)
                    logger.info(f"   - {email}: Bot={bot_status}")
                
                # Verificar si hay operaciones pendientes de replicar
                if hasattr(self.web_api, 'trader_instance') and self.web_api.trader_instance:
                    if hasattr(self.web_api.trader_instance, 'result_queue'):
                        queue_size = self.web_api.trader_instance.result_queue.qsize()
                        if queue_size > 0:
                            logger.warning(f"⚠️ Hay {queue_size} operaciones pendientes en la cola")
                
                time.sleep(25)
            except Exception as e:
                logger.error(f"❌ Error verificando lógica de replicación: {e}")
                time.sleep(25)
    
    def _log_summary(self):
        """Mostrar resumen del estado"""
        try:
            web_status = self.web_api.get_status()
            trader = web_status.get('trader', {})
            followers = web_status.get('followers', [])
            auto_copy = self.web_api.is_auto_copy_active()
            
            logger.info("=" * 60)
            logger.info("📊 RESUMEN DEL ESTADO DEL BOT WEB")
            logger.info(f"🤖 Trader conectado: {trader.get('connected', False)}")
            logger.info(f"👥 Seguidores: {len(followers)}")
            logger.info(f"🔄 Auto copy activo: {auto_copy}")
            logger.info(f"📡 Auto copy followers: {len(getattr(self.web_api, 'auto_copy_followers', []))}")
            
            # Verificar bots de seguidores
            active_bots = 0
            for follower in followers:
                email = follower.get('email', 'unknown')
                if self.web_api.get_follower_bot_status(email):
                    active_bots += 1
            
            logger.info(f"🤖 Bots de seguidores activos: {active_bots}/{len(followers)}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")
    
    def test_web_api_endpoints(self):
        """Probar endpoints del bot web"""
        try:
            # Probar endpoint de estado
            response = requests.get(f"{self.web_base_url}/api/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Endpoint /api/status funcionando")
            else:
                logger.warning(f"⚠️ Endpoint /api/status devolvió código {response.status_code}")
            
            # Probar endpoint de trader
            response = requests.get(f"{self.web_base_url}/api/trader/status", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Endpoint /api/trader/status funcionando")
            else:
                logger.warning(f"⚠️ Endpoint /api/trader/status devolvió código {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Error probando endpoints: {e}")

def main():
    """Función principal del monitor"""
    logger.info("🚀 Iniciando Monitor de Comparación Bot Web vs Original")
    logger.info("=" * 70)
    
    monitor = BotComparisonMonitor()
    
    # Probar endpoints primero
    monitor.test_web_api_endpoints()
    
    # Iniciar monitoreo
    monitor.start_monitoring()

if __name__ == "__main__":
    main()

