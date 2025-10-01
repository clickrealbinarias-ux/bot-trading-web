#!/usr/bin/env python3
"""
MONITOR SIMPLE DEL BOT WEB
Monitorea el estado del bot web para detectar problemas de replicación
"""

import sys
import os
import time
import json
import logging
import requests
from datetime import datetime
import threading

# Agregar el directorio exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SimpleWebBotMonitor:
    """Monitor simple del bot web"""
    
    def __init__(self):
        self.web_base_url = "http://localhost:5003"
        self.monitoring = False
        self.last_operation_time = None
        self.operation_count = 0
        
        logger.info("🔍 Monitor simple del bot web inicializado")
    
    def start_monitoring(self):
        """Iniciar monitoreo"""
        self.monitoring = True
        logger.info("🚀 Iniciando monitoreo del bot web...")
        
        # Crear threads para diferentes verificaciones
        threads = [
            threading.Thread(target=self._monitor_web_status, daemon=True),
            threading.Thread(target=self._monitor_trader_status, daemon=True),
            threading.Thread(target=self._monitor_followers_status, daemon=True),
            threading.Thread(target=self._monitor_auto_copy_status, daemon=True),
            threading.Thread(target=self._monitor_operations, daemon=True)
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
    
    def _monitor_web_status(self):
        """Monitorear estado general del bot web"""
        while self.monitoring:
            try:
                response = requests.get(f"{self.web_base_url}/api/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"🌐 Bot web activo - Seguidores: {data.get('followers_count', 0)}")
                else:
                    logger.warning(f"⚠️ Bot web respondió con código {response.status_code}")
                
                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ Error verificando estado del bot web: {e}")
                time.sleep(30)
    
    def _monitor_trader_status(self):
        """Monitorear estado del trader"""
        while self.monitoring:
            try:
                response = requests.get(f"{self.web_base_url}/api/trader/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    trader_status = data.get('trader_status', {})
                    connected = trader_status.get('connected', False)
                    auto_copy = data.get('auto_copy_active', False)
                    
                    logger.info(f"🤖 Trader: Conectado={connected}, Auto Copy={auto_copy}")
                    
                    if not connected:
                        logger.warning("⚠️ Trader NO está conectado")
                    if not auto_copy:
                        logger.warning("⚠️ Auto Copy NO está activo")
                else:
                    logger.warning(f"⚠️ Error obteniendo estado del trader: {response.status_code}")
                
                time.sleep(15)
            except Exception as e:
                logger.error(f"❌ Error verificando trader: {e}")
                time.sleep(15)
    
    def _monitor_followers_status(self):
        """Monitorear estado de los seguidores"""
        while self.monitoring:
            try:
                # Obtener lista de seguidores
                response = requests.get(f"{self.web_base_url}/api/followers", timeout=5)
                if response.status_code == 200:
                    followers = response.json().get('followers', [])
                    
                    active_bots = 0
                    for follower in followers:
                        email = follower.get('email', 'unknown')
                        bot_status = follower.get('bot_status', False)
                        connected = follower.get('connected', False)
                        
                        if bot_status:
                            active_bots += 1
                        
                        logger.info(f"👤 {email}: Conectado={connected}, Bot={bot_status}")
                    
                    logger.info(f"📊 Seguidores con bot activo: {active_bots}/{len(followers)}")
                    
                    if active_bots == 0 and len(followers) > 0:
                        logger.warning("⚠️ NINGÚN seguidor tiene el bot activo")
                else:
                    logger.warning(f"⚠️ Error obteniendo seguidores: {response.status_code}")
                
                time.sleep(20)
            except Exception as e:
                logger.error(f"❌ Error verificando seguidores: {e}")
                time.sleep(20)
    
    def _monitor_auto_copy_status(self):
        """Monitorear estado del auto copy"""
        while self.monitoring:
            try:
                response = requests.get(f"{self.web_base_url}/api/trader/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    auto_copy = data.get('auto_copy_active', False)
                    
                    if auto_copy:
                        logger.info("🔄 Auto Copy está ACTIVO")
                    else:
                        logger.warning("⚠️ Auto Copy está INACTIVO")
                else:
                    logger.warning(f"⚠️ Error verificando auto copy: {response.status_code}")
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"❌ Error verificando auto copy: {e}")
                time.sleep(10)
    
    def _monitor_operations(self):
        """Monitorear operaciones detectadas"""
        while self.monitoring:
            try:
                # Leer logs del bot web para detectar operaciones
                log_file = "copytrading_web.log"
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    
                    # Buscar operaciones recientes (últimas 10 líneas)
                    recent_lines = lines[-10:] if len(lines) >= 10 else lines
                    
                    for line in recent_lines:
                        if "NUEVA OPERACIÓN DETECTADA" in line:
                            self.operation_count += 1
                            self.last_operation_time = datetime.now()
                            logger.info(f"🎯 OPERACIÓN DETECTADA #{self.operation_count}: {line.strip()}")
                        
                        if "Seguidor con bot APAGADO" in line:
                            logger.warning(f"⚠️ PROBLEMA: {line.strip()}")
                        
                        if "Replicando operación" in line:
                            logger.info(f"🔄 REPLICANDO: {line.strip()}")
                
                time.sleep(5)
            except Exception as e:
                logger.error(f"❌ Error monitoreando operaciones: {e}")
                time.sleep(5)
    
    def _log_summary(self):
        """Mostrar resumen del estado"""
        try:
            logger.info("=" * 60)
            logger.info("📊 RESUMEN DEL MONITOR")
            logger.info(f"🎯 Operaciones detectadas: {self.operation_count}")
            if self.last_operation_time:
                logger.info(f"⏰ Última operación: {self.last_operation_time.strftime('%H:%M:%S')}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")

def main():
    """Función principal del monitor"""
    logger.info("🚀 Iniciando Monitor Simple del Bot Web")
    logger.info("=" * 70)
    
    monitor = SimpleWebBotMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()

