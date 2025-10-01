#!/usr/bin/env python3
"""
MONITOR DE PROCESOS DEL BOT WEB
Verifica que se estén ejecutando los mismos procesos que el bot de ejemplo
Solo observa, no hace login automático - el usuario debe iniciar sesión desde la web
"""

import sys
import os
import time
import json
import logging
import requests
from datetime import datetime
import threading
import psutil

# Agregar el directorio exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('process_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProcessMonitor:
    """Monitor de procesos del bot web"""
    
    def __init__(self):
        self.web_base_url = "http://localhost:5003"
        self.monitoring = False
        self.processes_found = []
        self.last_check = None
        
        logger.info("🔍 Monitor de procesos del bot web inicializado")
        logger.info("ℹ️  Este monitor solo OBSERVA - debes iniciar sesión desde la web")
    
    def start_monitoring(self):
        """Iniciar monitoreo de procesos"""
        self.monitoring = True
        logger.info("🚀 Iniciando monitoreo de procesos...")
        logger.info("=" * 70)
        logger.info("📋 INSTRUCCIONES:")
        logger.info("1. Abre http://localhost:5003 en tu navegador")
        logger.info("2. Inicia sesión como trader")
        logger.info("3. Inicia sesión como seguidor")
        logger.info("4. Activa el bot del seguidor")
        logger.info("5. Activa el auto copy")
        logger.info("6. Realiza una operación")
        logger.info("=" * 70)
        
        # Crear threads para diferentes verificaciones
        threads = [
            threading.Thread(target=self._monitor_web_connection, daemon=True),
            threading.Thread(target=self._monitor_python_processes, daemon=True),
            threading.Thread(target=self._monitor_exnova_connections, daemon=True),
            threading.Thread(target=self._monitor_websocket_connections, daemon=True),
            threading.Thread(target=self._monitor_log_files, daemon=True),
            threading.Thread(target=self._monitor_operations_detection, daemon=True)
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
    
    def _monitor_web_connection(self):
        """Monitorear conexión con el bot web"""
        while self.monitoring:
            try:
                response = requests.get(f"{self.web_base_url}/", timeout=5)
                if response.status_code == 200:
                    logger.info("🌐 Bot web: CONECTADO")
                else:
                    logger.warning(f"⚠️ Bot web respondió con código {response.status_code}")
                
                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ Error conectando con bot web: {e}")
                time.sleep(30)
    
    def _monitor_python_processes(self):
        """Monitorear procesos de Python relacionados con el bot"""
        while self.monitoring:
            try:
                # Buscar procesos de Python relacionados con el bot
                bot_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                            if 'app.py' in cmdline or 'our_copytrading_api' in cmdline:
                                bot_processes.append({
                                    'pid': proc.info['pid'],
                                    'cmdline': cmdline
                                })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if bot_processes:
                    logger.info(f"🐍 Procesos Python del bot encontrados: {len(bot_processes)}")
                    for proc in bot_processes:
                        logger.info(f"   PID {proc['pid']}: {proc['cmdline']}")
                else:
                    logger.warning("⚠️ No se encontraron procesos Python del bot")
                
                time.sleep(20)
            except Exception as e:
                logger.error(f"❌ Error monitoreando procesos Python: {e}")
                time.sleep(20)
    
    def _monitor_exnova_connections(self):
        """Monitorear conexiones con ExNova"""
        while self.monitoring:
            try:
                # Buscar conexiones de red relacionadas con ExNova
                exnova_connections = []
                for conn in psutil.net_connections():
                    if conn.raddr and conn.raddr.port in [443, 80]:  # HTTPS/HTTP
                        try:
                            # Verificar si es conexión a ExNova
                            if hasattr(conn, 'raddr') and conn.raddr:
                                exnova_connections.append({
                                    'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                                    'remote': f"{conn.raddr.ip}:{conn.raddr.port}",
                                    'status': conn.status
                                })
                        except:
                            continue
                
                if exnova_connections:
                    logger.info(f"🔗 Conexiones ExNova activas: {len(exnova_connections)}")
                    for conn in exnova_connections[:3]:  # Mostrar solo las primeras 3
                        logger.info(f"   {conn['local']} -> {conn['remote']} ({conn['status']})")
                else:
                    logger.info("ℹ️ No hay conexiones ExNova activas")
                
                time.sleep(25)
            except Exception as e:
                logger.error(f"❌ Error monitoreando conexiones ExNova: {e}")
                time.sleep(25)
    
    def _monitor_websocket_connections(self):
        """Monitorear conexiones websocket"""
        while self.monitoring:
            try:
                # Buscar conexiones websocket
                ws_connections = []
                for conn in psutil.net_connections():
                    if conn.laddr and conn.laddr.port == 5003:  # Puerto del bot web
                        ws_connections.append({
                            'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                            'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                            'status': conn.status
                        })
                
                if ws_connections:
                    logger.info(f"🔌 Conexiones WebSocket activas: {len(ws_connections)}")
                    for conn in ws_connections[:3]:  # Mostrar solo las primeras 3
                        logger.info(f"   {conn['local']} <- {conn['remote']} ({conn['status']})")
                else:
                    logger.info("ℹ️ No hay conexiones WebSocket activas")
                
                time.sleep(15)
            except Exception as e:
                logger.error(f"❌ Error monitoreando WebSocket: {e}")
                time.sleep(15)
    
    def _monitor_log_files(self):
        """Monitorear archivos de log para detectar actividad"""
        while self.monitoring:
            try:
                log_file = "copytrading_web.log"
                if os.path.exists(log_file):
                    # Leer las últimas 5 líneas del log
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                    
                    recent_lines = lines[-5:] if len(lines) >= 5 else lines
                    
                    for line in recent_lines:
                        line = line.strip()
                        if line:
                            # Detectar eventos importantes
                            if "NUEVA OPERACIÓN DETECTADA" in line:
                                logger.info(f"🎯 OPERACIÓN DETECTADA: {line}")
                            elif "Replicando operación" in line:
                                logger.info(f"🔄 REPLICANDO: {line}")
                            elif "Seguidor con bot APAGADO" in line:
                                logger.warning(f"⚠️ BOT APAGADO: {line}")
                            elif "ERROR" in line or "Error" in line:
                                logger.error(f"❌ ERROR: {line}")
                            elif "Websocket connected" in line:
                                logger.info(f"🔌 WEBSOCKET: {line}")
                            elif "Proceso independiente" in line:
                                logger.info(f"🚀 PROCESO: {line}")
                
                time.sleep(5)
            except Exception as e:
                logger.error(f"❌ Error monitoreando logs: {e}")
                time.sleep(5)
    
    def _monitor_operations_detection(self):
        """Monitorear detección de operaciones"""
        while self.monitoring:
            try:
                # Verificar si hay archivos de base de datos
                db_files = [
                    "database/followers.json",
                    "seguidores_database.json",
                    "operations.json"
                ]
                
                for db_file in db_files:
                    if os.path.exists(db_file):
                        # Leer tamaño del archivo
                        size = os.path.getsize(db_file)
                        logger.info(f"📊 Base de datos {db_file}: {size} bytes")
                        
                        # Si es un archivo JSON, intentar leer contenido
                        if db_file.endswith('.json'):
                            try:
                                with open(db_file, 'r') as f:
                                    data = json.load(f)
                                if isinstance(data, dict):
                                    for key, value in data.items():
                                        if isinstance(value, list):
                                            logger.info(f"   {key}: {len(value)} elementos")
                                        else:
                                            logger.info(f"   {key}: {value}")
                            except:
                                pass
                
                time.sleep(30)
            except Exception as e:
                logger.error(f"❌ Error monitoreando operaciones: {e}")
                time.sleep(30)
    
    def _log_summary(self):
        """Mostrar resumen del estado"""
        try:
            logger.info("=" * 60)
            logger.info("📊 RESUMEN DEL MONITOR DE PROCESOS")
            logger.info(f"⏰ Última verificación: {datetime.now().strftime('%H:%M:%S')}")
            
            # Verificar procesos Python
            python_processes = 0
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] in ['python', 'python3']:
                    python_processes += 1
            
            logger.info(f"🐍 Procesos Python activos: {python_processes}")
            
            # Verificar conexiones de red
            network_connections = len(psutil.net_connections())
            logger.info(f"🔗 Conexiones de red activas: {network_connections}")
            
            # Verificar archivos de log
            if os.path.exists("copytrading_web.log"):
                size = os.path.getsize("copytrading_web.log")
                logger.info(f"📝 Log del bot: {size} bytes")
            else:
                logger.warning("⚠️ Archivo de log no encontrado")
            
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen: {e}")

def main():
    """Función principal del monitor"""
    logger.info("🚀 Iniciando Monitor de Procesos del Bot Web")
    logger.info("=" * 70)
    
    monitor = ProcessMonitor()
    monitor.start_monitoring()

if __name__ == "__main__":
    main()

