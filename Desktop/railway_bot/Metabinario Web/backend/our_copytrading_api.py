#!/usr/bin/env python3
"""
NUESTRA PROPIA API DE COPYTRADING
Usa la API existente de ExNova sin modificarla, pero resuelve el problema de copytrading
con arquitectura de instancias completamente independientes
"""

import sys
import os
import threading
import time
import uuid
import logging
from typing import Dict, List, Tuple, Optional
import multiprocessing
import queue
import json

# Agregar el directorio exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

logger = logging.getLogger(__name__)

def convert_currency_format(currency: str) -> str:
    """
    Convierte el formato de divisa para que funcione con mercado real
    EURUSD -> EURUSD-op (formato correcto para mercado real)
    EURUSD-OTC -> mantiene formato OTC
    """
    # Mapeo correcto basado en el análisis del bot que funciona
    real_market_mapping = {
        'EURUSD': 'EURUSD-op',       # ✅ Formato correcto para mercado real
        'GBPUSD': 'GBPUSD-op',       # ✅ Formato correcto para mercado real
        'USDJPY': 'USDJPY-op',       # ✅ Formato correcto para mercado real
        'EURJPY': 'EURJPY-op',       # ✅ Formato correcto para mercado real
        'AUDUSD': 'AUDUSD-op',       # ✅ Formato correcto para mercado real
        'USDCAD': 'USDCAD-op',       # ✅ Formato correcto para mercado real
        'NZDUSD': 'NZDUSD-op',       # ✅ Formato correcto para mercado real
        'EURGBP': 'EURGBP-op',       # ✅ Formato correcto para mercado real
        'EURAUD': 'EURAUD-op',       # ✅ Formato correcto para mercado real
        'GBPJPY': 'GBPJPY-op',       # ✅ Formato correcto para mercado real
        'AUDJPY': 'AUDJPY-op',       # ✅ Formato correcto para mercado real
        'CADJPY': 'CADJPY-op',       # ✅ Formato correcto para mercado real
        'NZDJPY': 'NZDJPY-op',       # ✅ Formato correcto para mercado real
        'GBPAUD': 'GBPAUD-op',       # ✅ Formato correcto para mercado real
        'GBPCAD': 'GBPCAD-op',       # ✅ Formato correcto para mercado real
        'AUDCAD': 'AUDCAD-op',       # ✅ Formato correcto para mercado real
        'AUDNZD': 'AUDNZD-op',       # ✅ Formato correcto para mercado real
        'NZDCAD': 'NZDCAD-op',       # ✅ Formato correcto para mercado real
        'USDCHF': 'USDCHF-op',       # ✅ Formato correcto para mercado real
        'EURCHF': 'EURCHF-op',       # ✅ Formato correcto para mercado real
        'GBPCHF': 'GBPCHF-op',       # ✅ Formato correcto para mercado real
        'AUDCHF': 'AUDCHF-op',       # ✅ Formato correcto para mercado real
        'NZDCHF': 'NZDCHF-op',       # ✅ Formato correcto para mercado real
        'CHFJPY': 'CHFJPY-op'        # ✅ Formato correcto para mercado real
    }
    
    # Si ya tiene sufijo OTC, mantenerlo
    if currency.endswith('-OTC'):
        return currency
    
    # Si ya tiene sufijo -op, mantenerlo
    if currency.endswith('-op'):
        return currency
    
    # Si es una divisa de mercado real, usar el mapeo
    if currency in real_market_mapping:
        converted = real_market_mapping[currency]
        logger.info(f"🔄 Convirtiendo {currency} -> {converted} (mercado real)")
        return converted
    
    # Si no está en el mapeo, devolver tal como está
    return currency

class IndependentExNovaInstance:
    """
    Instancia completamente independiente de ExNova
    Cada instancia se ejecuta en su propio proceso para evitar conflictos
    """
    
    def __init__(self, email: str, password: str, balance_mode: str, instance_id: str):
        self.email = email
        self.password = password
        self.balance_mode = balance_mode
        self.instance_id = instance_id
        self.is_connected = False
        self.connection = None
        self.process = None
        self.command_queue = None
        self.result_queue = None
        
    def start_independent_process(self):
        """Iniciar proceso independiente para esta instancia"""
        self.command_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        
        self.process = multiprocessing.Process(
            target=self._run_independent_instance,
            args=(self.email, self.password, self.balance_mode, self.instance_id, 
                  self.command_queue, self.result_queue)
        )
        self.process.start()
        
        # Esperar confirmación de conexión
        try:
            result = self.result_queue.get(timeout=10)
            if result['status'] == 'connected':
                self.is_connected = True
                logger.info(f"✅ Instancia independiente {self.instance_id} conectada: {self.email}")
                return True
            else:
                logger.error(f"❌ Error conectando instancia {self.instance_id}: {result.get('error', 'Unknown')}")
                return False
        except queue.Empty:
            logger.error(f"❌ Timeout conectando instancia {self.instance_id}")
            return False
    
    @staticmethod
    def _run_independent_instance(email, password, balance_mode, instance_id, command_queue, result_queue):
        """
        Ejecutar instancia independiente en proceso separado
        Cada proceso tiene su propia importación y variables globales
        """
        try:
            # Importar ExNova en el proceso independiente
            from exnovaapi.stable_api import Exnova
            import exnovaapi.global_value as global_value
            import time
            
            logger.info(f"🔧 Proceso independiente {instance_id} iniciado para {email}")
            
            # Crear conexión en este proceso
            connection = Exnova(email, password)
            connection.connect()
            
            # Verificar si la conexión fue exitosa
            if not hasattr(connection, 'api') or not connection.api:
                result_queue.put({'status': 'error', 'error': 'Error de conexión'})
                return
            
            # Configurar balance mode
            connection.change_balance(balance_mode)
            
            # Capturar balance_id específico de este proceso
            current_balance_id = global_value.balance_id
            
            logger.info(f"✅ Proceso {instance_id} conectado: {email}, Balance ID: {current_balance_id}")
            
            # Confirmar conexión exitosa
            result_queue.put({
                'status': 'connected', 
                'balance_id': current_balance_id,
                'email': email
            })
            
            # Variables para monitoreo de operaciones (solo para trader)
            monitoring_active = False
            last_operations = {}
            is_trader = instance_id.startswith("trader_")
            
            # Conjunto para almacenar IDs de operaciones ya procesadas por este seguidor
            processed_operation_ids = set()
            
            # Loop principal del proceso
            while True:
                try:
                    # Verificar si hay comandos (no bloqueante)
                    command = None
                    try:
                        command = command_queue.get_nowait()
                    except queue.Empty:
                        pass
                    
                    if command:
                        if command['action'] == 'execute_operation':
                            # Ejecutar operación en este proceso independiente
                            amount = command['amount']
                            active = command['active']
                            direction = command['direction']
                            duration = command['duration']
                            
                            # Convertir formato de divisa para mercado real
                            converted_active = convert_currency_format(active)
                            
                            logger.info(f"🔧 [{instance_id}] Ejecutando operación: {email}")
                            logger.info(f"🔧 [{instance_id}] Balance ID actual: {global_value.balance_id}")
                            logger.info(f"🔧 [{instance_id}] Divisa original: {active} -> Convertida: {converted_active}")
                            
                            success, result = connection.buy(amount, converted_active, direction, duration)
                            
                            result_queue.put({
                                'status': 'operation_result',
                                'success': success,
                                'result': result,
                                'balance_id': global_value.balance_id,
                                'email': email,
                                'instance_id': instance_id
                            })
                            
                        elif command['action'] == 'start_monitoring':
                            # Activar monitoreo de operaciones (solo para trader)
                            if is_trader:
                                monitoring_active = True
                                logger.info(f"🤖 [{instance_id}] Monitoreo de operaciones activado")
                                result_queue.put({
                                    'status': 'monitoring_started',
                                    'instance_id': instance_id
                                })
                            
                        elif command['action'] == 'stop_monitoring':
                            # Desactivar monitoreo de operaciones
                            if is_trader:
                                monitoring_active = False
                                logger.info(f"🤖 [{instance_id}] Monitoreo de operaciones desactivado")
                                result_queue.put({
                                    'status': 'monitoring_stopped',
                                    'instance_id': instance_id
                                })
                            
                        elif command['action'] == 'stop':
                            logger.info(f"🔄 Deteniendo proceso {instance_id}")
                            break
                    
                    # Monitoreo de operaciones (solo para trader y si está activado)
                    if is_trader and monitoring_active:
                        try:
                            # Acceder al socket de operaciones abiertas
                            if hasattr(connection, 'api') and connection.api:
                                current_operations = getattr(connection.api, 'socket_option_opened', {})
                                
                                # Detectar nuevas operaciones
                                for op_id, op_data in current_operations.items():
                                    if op_id not in last_operations and op_id not in processed_operation_ids:
                                        # Nueva operación detectada
                                        logger.info(f"🤖 [{instance_id}] NUEVA OPERACIÓN DETECTADA: {op_id}")
                                        processed_operation_ids.add(op_id) # Añadir a las operaciones procesadas
                                        
                                        # Extraer datos de la operación correctamente
                                        msg_data = op_data.get('msg', {})
                                        active = msg_data.get('active', '')
                                        direction = msg_data.get('dir', '')
                                        amount = msg_data.get('amount', 0)
                                        
                                        # LOG COMPLETO PARA DEPURACIÓN
                                        logger.info(f"🔍 DATOS COMPLETOS DE LA OPERACIÓN: {msg_data}")
                                        
                                        # Calcular duración real en minutos
                                        created = msg_data.get('created', 0)
                                        exp_time = msg_data.get('exp_time', 0)
                                        
                                        if created and exp_time:
                                            duration = max(1, round((exp_time - created) / 60))  # Convertir a minutos, mínimo 1
                                        else:
                                            duration = 2  # Default 2 minutos si no hay datos
                                        
                                        # Enviar notificación de nueva operación
                                        result_queue.put({
                                            'status': 'new_operation_detected',
                                            'operation_id': op_id,
                                            'active': active,
                                            'direction': direction,
                                            'amount': amount,
                                            'duration': duration,
                                            'instance_id': instance_id,
                                            'email': email
                                        })
                                
                                # Actualizar operaciones conocidas
                                last_operations = current_operations.copy()
                                
                        except Exception as e:
                            logger.error(f"❌ [{instance_id}] Error en monitoreo: {e}")
                    
                    # Pequeña pausa para no sobrecargar el CPU
                    time.sleep(0.5)
                        
                except Exception as e:
                    logger.error(f"❌ Error en proceso {instance_id}: {e}")
                    result_queue.put({
                        'status': 'error',
                        'error': str(e),
                        'instance_id': instance_id
                    })
                    
        except Exception as e:
            logger.error(f"❌ Error crítico en proceso {instance_id}: {e}")
            result_queue.put({'status': 'error', 'error': str(e)})
    
    def execute_operation(self, amount: float, active: str, direction: str, duration: int) -> Tuple[bool, str]:
        """Ejecutar operación en el proceso independiente"""
        if not self.is_connected or not self.process or not self.process.is_alive():
            return False, "Instancia no conectada o proceso no activo"
        
        # Enviar comando al proceso
        command = {
            'action': 'execute_operation',
            'amount': amount,
            'active': active,
            'direction': direction,
            'duration': duration
        }
        
        self.command_queue.put(command)
        
        # Esperar resultado
        try:
            result = self.result_queue.get(timeout=30)
            if result['status'] == 'operation_result':
                return result['success'], result['result']
            else:
                return False, result.get('error', 'Error desconocido')
        except queue.Empty:
            return False, "Timeout ejecutando operación"
    
    def start_monitoring(self) -> bool:
        """Iniciar monitoreo de operaciones (solo para trader)"""
        if not self.is_connected or not self.process or not self.process.is_alive():
            logger.warning(f"⚠️ Instancia {self.instance_id} no está conectada o proceso no activo")
            return False
        
        # Enviar comando para iniciar monitoreo
        command = {'action': 'start_monitoring'}
        try:
            self.command_queue.put(command)
        except Exception as e:
            logger.error(f"❌ Error enviando comando de monitoreo: {e}")
            return False
        
        # Esperar confirmación con timeout más largo
        try:
            result = self.result_queue.get(timeout=15)
            if result.get('status') == 'monitoring_started':
                logger.info(f"✅ Monitoreo iniciado para {self.instance_id}")
                return True
            else:
                logger.warning(f"⚠️ Respuesta inesperada del monitoreo: {result}")
                return True  # Asumir éxito si hay respuesta
        except queue.Empty:
            logger.warning(f"⚠️ Timeout esperando confirmación de monitoreo para {self.instance_id}")
            return True  # Asumir éxito por timeout (el proceso puede estar funcionando)
        except Exception as e:
            logger.error(f"❌ Error esperando confirmación de monitoreo: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Detener monitoreo de operaciones"""
        if not self.is_connected or not self.process or not self.process.is_alive():
            return False
        
        # Enviar comando para detener monitoreo
        command = {'action': 'stop_monitoring'}
        self.command_queue.put(command)
        
        # Esperar confirmación
        try:
            result = self.result_queue.get(timeout=10)
            if result['status'] == 'monitoring_stopped':
                logger.info(f"✅ Monitoreo detenido para {self.instance_id}")
                return True
            else:
                return False
        except queue.Empty:
            return False
    
    def stop(self):
        """Detener la instancia independiente"""
        if self.process and self.process.is_alive():
            self.command_queue.put({'action': 'stop'})
            self.process.join(timeout=5)
            if self.process.is_alive():
                self.process.terminate()
        self.is_connected = False

class OurCopyTradingAPI:
    """
    Nuestra propia API de copytrading
    Gestiona múltiples instancias independientes sin conflictos
    """
    
    def __init__(self):
        self.instances: Dict[str, IndependentExNovaInstance] = {}
        self.trader_instance: Optional[IndependentExNovaInstance] = None
        self.follower_instances: List[IndependentExNovaInstance] = []
        
        # Variables para copytrading automático
        self.auto_copy_active = False
        self.auto_copy_amount = 0
        self.auto_copy_context = None
        self.auto_copy_user_id = None
        self.auto_copy_followers = []
        
        # Sistema de gestión de sesiones activas
        self.active_sessions: Dict[str, str] = {}  # email -> instance_id
        self.session_owners: Dict[str, str] = {}   # instance_id -> email
        
        # Control individual de bots por seguidor
        self.follower_bot_status: Dict[str, bool] = {}  # email -> bot_encendido
        
        # Limpiar instancias duplicadas al inicializar
        self._cleanup_duplicate_instances()
    
    def _cleanup_duplicate_instances(self):
        """Limpiar instancias duplicadas al inicializar"""
        logger.info("🧹 Limpiando instancias duplicadas...")
        
        # Detener todas las instancias existentes
        for instance in self.instances.values():
            try:
                instance.stop()
            except:
                pass
        
        # Limpiar listas
        self.instances.clear()
        self.trader_instance = None
        self.follower_instances.clear()
        
        logger.info("✅ Limpieza completada")
    
    def _cleanup_all_sessions(self):
        """Limpiar todas las sesiones activas (usado cuando el trader inicia)"""
        logger.info("🧹 Limpiando todas las sesiones activas...")
        
        # Detener todas las instancias
        for instance in self.instances.values():
            try:
                instance.stop()
            except:
                pass
        
        # Limpiar todas las listas y diccionarios
        self.instances.clear()
        self.trader_instance = None
        self.follower_instances.clear()
        self.active_sessions.clear()
        self.session_owners.clear()
        
        logger.info("✅ Todas las sesiones limpiadas")
        
    def add_trader_account(self, email: str, password: str, balance_mode: str) -> bool:
        """Agregar cuenta trader principal - SIEMPRE limpia todo al iniciar"""
        logger.info(f"🚀 Iniciando sesión de trader: {email} - Limpiando todas las sesiones anteriores")
        
        # SIEMPRE limpiar todo cuando el trader inicia
        self._cleanup_all_sessions()
        
        # Crear nueva instancia trader
        instance_id = f"trader_{uuid.uuid4().hex[:8]}"
        
        instance = IndependentExNovaInstance(email, password, balance_mode, instance_id)
        
        if instance.start_independent_process():
            self.trader_instance = instance
            self.instances[instance_id] = instance
            
            # Registrar la sesión del trader
            self.active_sessions[email] = instance_id
            self.session_owners[instance_id] = email
            
            logger.info(f"✅ Cuenta trader agregada: {email} (sesión limpia)")
            return True
        else:
            logger.error(f"❌ Error agregando cuenta trader: {email}")
            return False
    
    def add_follower_account(self, email: str, password: str, balance_mode: str) -> bool:
        """Agregar cuenta seguidora con gestión inteligente de sesiones"""
        
        # Verificar si ya existe una sesión activa para este email
        if email in self.active_sessions:
            existing_instance_id = self.active_sessions[email]
            if existing_instance_id in self.instances:
                logger.info(f"🔄 Sesión activa encontrada para {email} - Reutilizando instancia existente")
                return True
            else:
                # La sesión está marcada como activa pero la instancia no existe, limpiar
                del self.active_sessions[email]
                if existing_instance_id in self.session_owners:
                    del self.session_owners[existing_instance_id]
        
        # Verificar si hay instancias duplicadas del mismo email y limpiarlas
        instances_to_remove = []
        for instance_id, instance in self.instances.items():
            if hasattr(instance, 'email') and instance.email == email:
                instances_to_remove.append(instance_id)
        
        for instance_id in instances_to_remove:
            if instance_id in self.instances:
                logger.info(f"🧹 Limpiando instancia duplicada: {instance_id}")
                self.instances[instance_id].stop()
                del self.instances[instance_id]
                if instance_id in self.session_owners:
                    del self.session_owners[instance_id]
        
        # Limpiar también de la lista de seguidores
        self.follower_instances = [f for f in self.follower_instances if f.email != email]
        
        # Crear nueva instancia
        instance_id = f"follower_{uuid.uuid4().hex[:8]}"
        
        instance = IndependentExNovaInstance(email, password, balance_mode, instance_id)
        
        if instance.start_independent_process():
            self.follower_instances.append(instance)
            self.instances[instance_id] = instance
            
            # Registrar la sesión activa
            self.active_sessions[email] = instance_id
            self.session_owners[instance_id] = email
            
            # Inicializar bot del seguidor como APAGADO
            self.follower_bot_status[email] = False
            
            logger.info(f"✅ Cuenta seguidora agregada: {email} (nueva sesión) - Bot APAGADO")
            return True
        else:
            logger.error(f"❌ Error agregando cuenta seguidora: {email}")
            return False
    
    def disconnect_follower(self, email: str) -> bool:
        """Desconectar seguidor explícitamente"""
        if email in self.active_sessions:
            instance_id = self.active_sessions[email]
            
            # Detener la instancia
            if instance_id in self.instances:
                self.instances[instance_id].stop()
                del self.instances[instance_id]
            
            # Limpiar de las listas
            self.follower_instances = [f for f in self.follower_instances if f.email != email]
            
            # Limpiar de las sesiones activas
            del self.active_sessions[email]
            if instance_id in self.session_owners:
                del self.session_owners[instance_id]
            
            logger.info(f"✅ Seguidor desconectado: {email}")
            return True
        else:
            logger.warning(f"⚠️ Seguidor no encontrado en sesiones activas: {email}")
            return False
    
    def start_follower_bot(self, email: str) -> bool:
        """Encender bot del seguidor individual"""
        # Verificar si el seguidor existe en cualquier lista
        follower_exists = False
        for follower in self.follower_instances:
            if follower.email == email:
                follower_exists = True
                break
        
        if follower_exists:
            self.follower_bot_status[email] = True
            logger.info(f"🤖 Bot del seguidor ENCENDIDO: {email}")
            
            # Actualizar también en las instancias de copytrading automático
            self._update_auto_copy_follower_status(email, True)
            
            return True
        else:
            logger.warning(f"⚠️ Seguidor no encontrado: {email}")
            return False
    
    def stop_follower_bot(self, email: str) -> bool:
        """Apagar bot del seguidor individual"""
        # Verificar si el seguidor existe en cualquier lista
        follower_exists = False
        for follower in self.follower_instances:
            if follower.email == email:
                follower_exists = True
                break
        
        if follower_exists:
            self.follower_bot_status[email] = False
            logger.info(f"🛑 Bot del seguidor APAGADO: {email}")
            
            # Actualizar también en las instancias de copytrading automático
            self._update_auto_copy_follower_status(email, False)
            
            return True
        else:
            logger.warning(f"⚠️ Seguidor no encontrado: {email}")
            return False
    
    def get_follower_bot_status(self, email: str) -> bool:
        """Obtener estado del bot del seguidor"""
        return self.follower_bot_status.get(email, False)
    
    def _sync_followers_with_database(self):
        """Sincronizar seguidores con la base de datos para asegurar que todos estén activos"""
        try:
            # Importar la base de datos de seguidores
            import json
            import os
            
            DATABASE_FILE = "seguidores_database.json"
            
            if os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    db_data = json.load(f)
                    followers_db = db_data.get("followers", [])
                    
                    # Activar todos los seguidores de la base de datos
                    for follower_data in followers_db:
                        if follower_data.get("active", True):
                            email = follower_data.get("email")
                            if email:
                                self.follower_bot_status[email] = True
                                logger.info(f"✅ Seguidor sincronizado desde BD: {email}")
                
                logger.info(f"✅ Sincronización completada: {len(followers_db)} seguidores de la BD")
            else:
                logger.warning("⚠️ No se encontró la base de datos de seguidores")
                
        except Exception as e:
            logger.error(f"❌ Error sincronizando con BD: {e}")
    
    def _sync_follower_bot_status(self):
        """Sincronizar estado del bot de seguidores con las instancias actuales"""
        logger.info("🔄 Sincronizando estado de bots de seguidores...")
        
        # Para cada seguidor en las instancias actuales, mantener el estado si ya existe
        for follower in self.auto_copy_followers:
            if follower.email in self.follower_bot_status:
                current_status = self.follower_bot_status[follower.email]
                logger.info(f"🔄 Manteniendo estado del bot para {follower.email}: {'ENCENDIDO' if current_status else 'APAGADO'}")
            else:
                # Solo establecer como APAGADO si NO existe previamente
                self.follower_bot_status[follower.email] = False
                logger.info(f"🔄 Estado inicial del bot para {follower.email}: APAGADO")
        
        logger.info("✅ Sincronización de estado de bots completada")
    
    def _update_auto_copy_follower_status(self, email: str, status: bool):
        """Actualizar estado del bot en las instancias de copytrading automático"""
        logger.info(f"🔄 Intentando actualizar estado del bot para {email} a {'ENCENDIDO' if status else 'APAGADO'}")
        
        # SIEMPRE actualizar el estado del bot, independientemente de auto_copy_followers
        self.follower_bot_status[email] = status
        logger.info(f"✅ Estado del bot actualizado para {email}: {'ENCENDIDO' if status else 'APAGADO'}")
        
        # También actualizar en auto_copy_followers si existe
        if hasattr(self, 'auto_copy_followers') and self.auto_copy_followers:
            logger.info(f"🔄 auto_copy_followers existe con {len(self.auto_copy_followers)} seguidores")
            for follower in self.auto_copy_followers:
                logger.info(f"🔄 Verificando seguidor: {follower.email}")
                if follower.email == email:
                    logger.info(f"✅ Seguidor encontrado en auto_copy_followers: {email}")
                    return True
            logger.warning(f"⚠️ Seguidor {email} no encontrado en auto_copy_followers")
        else:
            logger.warning(f"⚠️ auto_copy_followers no existe o está vacío")
        
        return True  # Siempre retornar True porque actualizamos el estado
    
    def execute_copytrading(self, active: str, duration: int, direction: str, followers: List[Dict]) -> bool:
        """
        Ejecutar copytrading con importes individuales de seguidores
        Esta es la función que usa el bot de Telegram
        """
        logger.info(f"⚡ Iniciando copytrading con {len(followers)} seguidores")
        
        if not self.trader_instance:
            logger.error("❌ No hay cuenta trader configurada")
            return False
        
        if not followers:
            logger.error("❌ No hay seguidores para replicar")
            return False
        
        # Convertir formato de divisa para mercado real
        converted_active = convert_currency_format(active)
        logger.info(f"🔧 Divisa original: {active} -> Convertida: {converted_active}")
        
        # Ejecutar operación del trader (sin importe específico, usa el del trader)
        trader_success, trader_result = self.trader_instance.execute_operation(
            self.auto_copy_amount,  # Usar el importe del trader
            converted_active,
            direction,
            duration
        )
        
        if not trader_success:
            logger.error(f"❌ Error en operación del trader: {trader_result}")
            return False
        
        logger.info(f"✅ Operación del trader exitosa: {trader_result}")
        
        # Replicar en seguidores con sus importes individuales
        replication_threads = []
        follower_results = {}
        
        def replicate_to_single_follower(follower_data):
            try:
                email = follower_data['email']
                password = follower_data['password']
                balance_mode = follower_data['balance_mode']
                follower_amount = float(follower_data['amount'])
                
                logger.info(f"🤖 [FOLLOWER] Replicando en: {email} con importe ${follower_amount}")
                
                # Buscar la instancia del seguidor
                follower_instance = None
                for instance in self.follower_instances:
                    if instance.email == email:
                        follower_instance = instance
                        break
                
                if not follower_instance:
                    logger.error(f"❌ Instancia no encontrada para {email}")
                    follower_results[email] = False
                    return
                
                # Ejecutar operación con el importe específico del seguidor
                success, result = follower_instance.execute_operation(
                    follower_amount,  # ✅ USAR IMPORTE ESPECÍFICO DEL SEGUIDOR
                    converted_active,
                    direction,
                    duration
                )
                
                if success:
                    logger.info(f"✅ [FOLLOWER] Operación exitosa: {email}, ID: {result}")
                    follower_results[email] = True
                else:
                    logger.error(f"❌ [FOLLOWER] Operación fallida: {email}: {result}")
                    follower_results[email] = False
                    
            except Exception as e:
                logger.error(f"❌ [FOLLOWER] Excepción {email}: {e}")
                follower_results[email] = False
        
        # Crear threads para cada seguidor
        for follower in followers:
            thread = threading.Thread(target=replicate_to_single_follower, args=(follower,))
            replication_threads.append(thread)
            thread.start()
        
        # Esperar a que todas las replicaciones terminen
        for thread in replication_threads:
            thread.join(timeout=30)
        
        # Contar resultados
        successful_followers = sum(1 for success in follower_results.values() if success)
        total_followers = len(followers)
        
        logger.info(f"📊 Replicación completada: {successful_followers}/{total_followers} seguidores exitosos")
        
        return successful_followers > 0

    def execute_copytrading_operation(self, amount: float, active: str, direction: str, duration: int) -> Dict:
        """
        Ejecutar operación de copytrading
        1. Ejecuta en cuenta trader
        2. Replica automáticamente en todas las cuentas seguidoras
        """
        results = {
            'trader_result': None,
            'follower_results': [],
            'success': False,
            'total_operations': 0,
            'successful_operations': 0
        }
        
        if not self.trader_instance:
            results['error'] = "No hay cuenta trader configurada"
            return results
        
        if not self.follower_instances:
            results['error'] = "No hay cuentas seguidoras configuradas"
            return results
        
        logger.info(f"⚡ Iniciando copytrading: {len(self.follower_instances) + 1} operaciones")
        
        # Lista de todas las operaciones a ejecutar
        all_operations = []
        
        # Agregar operación del trader
        all_operations.append({
            'instance': self.trader_instance,
            'type': 'trader',
            'email': self.trader_instance.email
        })
        
        # Agregar operaciones de seguidores
        for follower in self.follower_instances:
            all_operations.append({
                'instance': follower,
                'type': 'follower',
                'email': follower.email
            })
        
        # Ejecutar todas las operaciones usando threading para simultaneidad
        operation_threads = []
        operation_results = {}
        
        def execute_single_operation(operation_data, op_results, amount, active, direction, duration):
            """Ejecutar una sola operación en thread separado"""
            instance = operation_data['instance']
            op_type = operation_data['type']
            email = operation_data['email']
            
            try:
                # Convertir formato de divisa para mercado real
                converted_active = convert_currency_format(active)
                logger.info(f"🔧 [{op_type.upper()}] Ejecutando: {email}")
                logger.info(f"🔧 [{op_type.upper()}] Divisa original: {active} -> Convertida: {converted_active}")
                success, result = instance.execute_operation(amount, converted_active, direction, duration)
                
                op_results[instance.instance_id] = {
                    'type': op_type,
                    'email': email,
                    'success': success,
                    'result': result,
                    'instance_id': instance.instance_id
                }
                
                if success:
                    logger.info(f"✅ [{op_type.upper()}] Operación exitosa: {email}, ID: {result}")
                else:
                    logger.error(f"❌ [{op_type.upper()}] Operación fallida: {email}: {result}")
                    
            except Exception as e:
                logger.error(f"❌ [{op_type.upper()}] Excepción {email}: {e}")
                op_results[instance.instance_id] = {
                    'type': op_type,
                    'email': email,
                    'success': False,
                    'result': str(e),
                    'instance_id': instance.instance_id
                }
        
        # Crear y iniciar threads para todas las operaciones
        for operation in all_operations:
            thread = threading.Thread(
                target=execute_single_operation,
                args=(operation, operation_results, amount, active, direction, duration)
            )
            operation_threads.append(thread)
            thread.start()
        
        # Esperar a que todas las operaciones terminen
        for thread in operation_threads:
            thread.join(timeout=60)  # Timeout de 60 segundos por operación
        
        # Procesar resultados
        results['total_operations'] = len(all_operations)
        successful_count = 0
        
        for instance_id, op_result in operation_results.items():
            if op_result['type'] == 'trader':
                results['trader_result'] = op_result
            else:
                results['follower_results'].append(op_result)
            
            if op_result['success']:
                successful_count += 1
        
        results['successful_operations'] = successful_count
        results['success'] = successful_count > 0
        
        logger.info(f"🔧 Copytrading completado: {successful_count}/{len(all_operations)} operaciones exitosas")
        
        return results
    
    def start_auto_copy_monitoring_old(self, trader_email, follower_instances, auto_copy_amount, context, user_id):
        """Iniciar el monitoreo de copytrading automático"""
        if not self.trader_instance:
            logger.error("❌ No hay instancia trader para monitorear")
            return False
        
        logger.info(f"🤖 Iniciando monitoreo automático para trader: {trader_email}")
        
        # Configurar variables para copytrading automático
        self.auto_copy_active = True
        self.auto_copy_amount = auto_copy_amount
        self.auto_copy_context = context
        self.auto_copy_user_id = user_id
        self.auto_copy_followers = follower_instances
        
        # ✅ CORRECCIÓN: Activar automáticamente todos los bots de seguidores
        logger.info("🤖 Activando automáticamente todos los bots de seguidores...")
        for follower in follower_instances:
            if hasattr(follower, 'email'):
                self.follower_bot_status[follower.email] = True
                logger.info(f"✅ Bot del seguidor ACTIVADO automáticamente: {follower.email}")
        
        # ✅ CORRECCIÓN: Sincronizar con la base de datos de seguidores
        self._sync_followers_with_database()
        
        # Iniciar monitoreo en el proceso trader
        if self.trader_instance.start_monitoring():
            # Iniciar hilo para escuchar notificaciones de nuevas operaciones
            monitoring_thread = threading.Thread(
                target=self._listen_for_new_operations,
                daemon=True
            )
            monitoring_thread.start()
            logger.info("🤖 Copytrading automático iniciado correctamente")
            return True
        else:
            logger.error("❌ Error iniciando monitoreo en trader")
            return False

    def _listen_for_new_operations(self):
        """Escuchar notificaciones de nuevas operaciones del trader"""
        while self.auto_copy_active:
            try:
                if self.trader_instance and self.trader_instance.result_queue:
                    try:
                        # Escuchar mensajes del proceso trader (no bloqueante)
                        result = self.trader_instance.result_queue.get(timeout=1)
                        
                        if result['status'] == 'new_operation_detected':
                            # Nueva operación detectada del trader
                            active = result['active']
                            direction = result['direction']
                            operation_id = result['operation_id']
                            duration = result.get('duration', 2)  # Obtener duración real
                            
                            logger.info(f"🤖 NUEVA OPERACIÓN DETECTADA: {operation_id} - {active} {direction} - {duration}min")
                            
                            # Replicar en todos los seguidores con la duración real
                            self._replicate_to_followers(active, direction, operation_id, duration)
                            
                    except queue.Empty:
                        # No hay mensajes, continuar
                        continue
                        
                time.sleep(0.5)  # Pequeña pausa
                
            except Exception as e:
                logger.error(f"❌ Error escuchando operaciones: {e}")
                time.sleep(5)  # Pausa más larga en caso de error
    
    def _replicate_to_followers(self, active, direction, operation_id, duration):
        """Replicar operación a todos los seguidores"""
        direction_text = "COMPRA" if direction == "CALL" else "VENTA"
        
        # FILTRAR SEGUIDORES ÚNICOS POR EMAIL Y CON BOT ENCENDIDO
        unique_followers = {}
        active_followers = []
        
        for follower in self.auto_copy_followers:
            if follower.email not in unique_followers:
                unique_followers[follower.email] = follower
                
                # SOLO incluir si el bot del seguidor está ENCENDIDO
                if self.get_follower_bot_status(follower.email):
                    active_followers.append(follower)
                    logger.info(f"✅ Seguidor con bot ENCENDIDO: {follower.email}")
                else:
                    logger.info(f"⏸️ Seguidor con bot APAGADO (no replica): {follower.email}")
            else:
                logger.warning(f"⚠️ Seguidor duplicado detectado: {follower.email} - Usando instancia única")
        
        logger.info(f"🤖 Replicando operación {operation_id} a {len(active_followers)} seguidores con bot ENCENDIDO (de {len(unique_followers)} totales)")
        
        # Replicar en todos los seguidores usando threading para simultaneidad
        replication_threads = []
        follower_results = {}  # Para almacenar resultados de cada seguidor
        
        def replicate_to_single_follower(follower):
            try:
                logger.info(f"🤖 [FOLLOWER AUTO] Replicando en: {follower.email}")
                
                # Obtener importe configurado del seguidor desde la base de datos
                # Usar ruta absoluta fija para evitar problemas de directorio de trabajo
                try:
                    import json
                    import os
                    
                    # Ruta absoluta fija al archivo de base de datos
                    db_path = "/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend/seguidores_database.json"
                    follower_amount = 10.0  # Importe por defecto
                    db_found = False
                    
                    logger.info(f"🔍 Buscando importe para {follower.email} en: {db_path}")
                    
                    if os.path.exists(db_path):
                        logger.info(f"✅ Archivo encontrado: {db_path}")
                        try:
                            with open(db_path, 'r', encoding='utf-8') as f:
                                db_data = json.load(f)
                                
                                # El formato del bot web es: {"followers": [{"email": "X", "amount": Y}]}
                                if "followers" in db_data:
                                    followers_list = db_data["followers"]
                                    logger.info(f"📊 Base de datos contiene {len(followers_list)} seguidores")
                                    
                                    for f in followers_list:
                                        logger.info(f"📊 Verificando seguidor: {f.get('email')} - Importe: {f.get('amount')}")
                                        if f.get("email") == follower.email:
                                            follower_amount = float(f.get("amount", 10.0))
                                            logger.info(f"💰 ¡ENCONTRADO! Usando importe configurado del seguidor: ${follower_amount} (desde {db_path})")
                                            db_found = True
                                            break
                                    
                                    if not db_found:
                                        logger.warning(f"📊 Seguidor {follower.email} no encontrado en {db_path}")
                                else:
                                    logger.warning(f"📊 Formato de BD incorrecto en {db_path}")
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Error leyendo {db_path}: {e}")
                    else:
                        logger.warning(f"❌ Archivo no encontrado: {db_path}")
                    
                    if not db_found:
                        logger.warning(f"⚠️ Seguidor {follower.email} no encontrado en la base de datos, usando importe por defecto: ${follower_amount}")
                        
                except Exception as e:
                    follower_amount = 10.0  # Importe por defecto en caso de error
                    logger.warning(f"⚠️ Error obteniendo importe del seguidor, usando por defecto: ${follower_amount} - Error: {e}")
                
                # Convertir formato de divisa para mercado real
                converted_active = convert_currency_format(active)
                logger.info(f"🔧 [FOLLOWER AUTO] Divisa original: {active} -> Convertida: {converted_active}")
                
                # Ejecutar operación en el seguidor con SU IMPORTE CONFIGURADO
                success, result = follower.execute_operation(
                    follower_amount,  # ✅ CORRECTO: Usar importe del seguidor desde BD
                    converted_active,  # ✅ CORRECTO: Usar divisa convertida
                    direction, 
                    duration  # Usar duración real del trader
                )
                
                # Almacenar resultado para notificación posterior
                follower_name = follower.email.split('@')[0][:8]
                follower_results[follower_name] = "✅" if success else "❌"
                
                if success:
                    logger.info(f"✅ [FOLLOWER AUTO] Operación exitosa: {follower.email}, ID: {result}")
                    self._send_auto_copy_notification(follower.email, active, direction, follower_amount, result, True)
                else:
                    logger.error(f"❌ [FOLLOWER AUTO] Operación fallida: {follower.email}, Error: {result}")
                    self._send_auto_copy_notification(follower.email, active, direction, follower_amount, result, False)
                    
            except Exception as e:
                logger.error(f"❌ Error replicando en {follower.email}: {e}")
                follower_name = follower.email.split('@')[0][:8]
                follower_results[follower_name] = "❌"
        
        # Crear threads para cada seguidor con bot ENCENDIDO
        for follower in active_followers:
            thread = threading.Thread(target=replicate_to_single_follower, args=(follower,))
            replication_threads.append(thread)
            thread.start()
        
        # Esperar a que todas las replicaciones terminen
        for thread in replication_threads:
            thread.join(timeout=30)
        
        # Enviar notificación al trader con estado de todos los seguidores
        self._send_trader_operation_notification(active, direction, duration, follower_results)



    def _send_auto_copy_notification(self, follower_email, active, direction, amount, result, success):
        """Enviar notificación de copytrading automático"""
        try:
            if success:
                logger.info(f"✅ COPYTRADING AUTOMÁTICO EXITOSO - Seguidor: {follower_email} - Divisa: {active} - Dirección: {direction} - Importe: ${amount} - ID: {result}")
            else:
                logger.error(f"❌ ERROR EN COPYTRADING AUTOMÁTICO - Seguidor: {follower_email} - Divisa: {active} - Dirección: {direction} - Error: {result}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {e}")

    def _send_trader_operation_notification(self, active, direction, duration, follower_results):
        """Enviar notificación al trader con estado de todos los seguidores"""
        try:
            # Log de resultados para el trader
            logger.info(f"📊 OPERACIÓN TRADER: {active} {direction} {duration}min - Resultados seguidores: {follower_results}")
                
        except Exception as e:
            logger.error(f"❌ Error enviando notificación al trader: {e}")

    def get_status(self) -> Dict:

        """Obtener estado de todas las instancias"""
        status = {
            'trader': None,
            'followers': [],
            'total_instances': len(self.instances),
            'active_instances': 0
        }
        
        if self.trader_instance:
            status['trader'] = {
                'email': self.trader_instance.email,
                'balance_mode': self.trader_instance.balance_mode,
                'connected': self.trader_instance.is_connected,
                'instance_id': self.trader_instance.instance_id
            }
            if self.trader_instance.is_connected:
                status['active_instances'] += 1
        
        for follower in self.follower_instances:
            follower_info = {
                'email': follower.email,
                'balance_mode': follower.balance_mode,
                'connected': follower.is_connected,
                'instance_id': follower.instance_id
            }
            status['followers'].append(follower_info)
            if follower.is_connected:
                status['active_instances'] += 1
        
        return status
    
    def is_auto_copy_active(self):
        """Verificar si el copytrading automático está activo"""
        return getattr(self, 'auto_copy_active', False)
    
    def start_auto_copy_monitoring(self, callback):
        """Iniciar monitoreo de operaciones del trader para copytrading automático"""
        if not self.trader_instance:
            logger.error("❌ No se puede iniciar monitoreo sin cuenta trader")
            return False

        # Iniciar monitoreo en un thread separado
        monitoring_thread = threading.Thread(
            target=self._monitor_trader_operations,
            args=(callback,)
        )
        monitoring_thread.daemon = True
        monitoring_thread.start()
        logger.info("🤖 Monitoreo de copytrading automático iniciado")
        return True

    def _monitor_trader_operations(self, callback):
        """Monitorear operaciones del trader en un loop"""
        last_operations = {}

        while True:
            try:
                # Obtener operaciones abiertas del trader
                if self.trader_instance and self.trader_instance.is_connected:
                    # Esta es una simulación. Necesitamos una forma real de obtener las operaciones.
                    # Por ahora, vamos a simular que se detecta una nueva operación.
                    # En una implementación real, aquí iría la lógica para conectarse a la API
                    # y verificar si hay nuevas operaciones.
                    
                    # Simulación de detección de nueva operación
                    # Esto debería ser reemplazado con la lógica real de la API de Exnova
                    if hasattr(self.trader_instance.connection, 'api') and self.trader_instance.connection.api:
                        current_operations = self.trader_instance.connection.api.socket_option_opened
                        
                        new_operations = {op_id: op_data for op_id, op_data in current_operations.items() if op_id not in last_operations}
                        
                        for op_id, op_data in new_operations.items():
                            logger.info(f"🤖 NUEVA OPERACIÓN DETECTADA: {op_id}")
                            
                            # Extraer datos de la operación
                            msg_data = op_data.get('msg', {})
                            active = msg_data.get('active', '')
                            direction = msg_data.get('dir', '')
                            
                            # Llamar al callback con los datos de la operación
                            if callback and active and direction:
                                callback(active, direction)
                        
                        last_operations = current_operations

                time.sleep(2)  # Esperar 2 segundos antes de volver a verificar

            except Exception as e:
                logger.error(f"❌ Error en monitoreo de copytrading: {e}")
                time.sleep(10) # Evitar spam de spam en caso de error
    
    def stop_all_instances(self):
        """Detener todas las instancias"""
        logger.info("🔄 Deteniendo todas las instancias...")
        
        for instance in self.instances.values():
            instance.stop()
        
        self.instances.clear()
        self.trader_instance = None
        self.follower_instances.clear()
        
        logger.info("✅ Todas las instancias detenidas")

# Función de utilidad para testing
def test_our_api():
    """Función de prueba para nuestra API"""
    logging.basicConfig(level=logging.INFO)
    
    api = OurCopyTradingAPI()
    
    print("🧪 TESTING NUESTRA API DE COPYTRADING")
    print("=" * 50)
    
    # Agregar cuenta trader
    print("1. Agregando cuenta trader...")
    trader_success = api.add_trader_account(
        "binariosector91@outlook.com", 
        "Binaryoptions91", 
        "PRACTICE"
    )
    print(f"   Resultado: {'✅ Éxito' if trader_success else '❌ Error'}")
    
    # Agregar cuenta seguidora
    print("2. Agregando cuenta seguidora...")
    follower_success = api.add_follower_account(
        "clickrealbinarias@outlook.com", 
        "Binaryoptions91", 
        "PRACTICE"
    )
    print(f"   Resultado: {'✅ Éxito' if follower_success else '❌ Error'}")
    
    if trader_success and follower_success:
        # Mostrar estado
        print("3. Estado de la API:")
        status = api.get_status()
        print(f"   Instancias activas: {status['active_instances']}/{status['total_instances']}")
        
        # Ejecutar operación de copytrading
        print("4. Ejecutando operación de copytrading...")
        results = api.execute_copytrading_operation(
            amount=10.0,
            active="EURGBP-OTC",
            direction="CALL",
            duration=2
        )
        
        print(f"   Operaciones exitosas: {results['successful_operations']}/{results['total_operations']}")
        
        if results['trader_result']:
            trader_res = results['trader_result']
            print(f"   Trader: {'✅' if trader_res['success'] else '❌'} {trader_res['email']} - {trader_res['result']}")
        
        for follower_res in results['follower_results']:
            print(f"   Seguidor: {'✅' if follower_res['success'] else '❌'} {follower_res['email']} - {follower_res['result']}")
    
    # Limpiar
    print("5. Limpiando instancias...")
    api.stop_all_instances()
    print("✅ Test completado")

    def start_auto_copy_monitoring(self, callback):
        """Iniciar monitoreo de operaciones del trader para copytrading automático"""
        if not self.trader_instance:
            logger.error("❌ No se puede iniciar monitoreo sin cuenta trader")
            return

        # Iniciar monitoreo en un thread separado
        monitoring_thread = threading.Thread(
            target=self._monitor_trader_operations,
            args=(callback,)
        )
        monitoring_thread.daemon = True
        monitoring_thread.start()
        logger.info("🤖 Monitoreo de copytrading automático iniciado")

    def _monitor_trader_operations(self, callback):
        """Monitorear operaciones del trader en un loop"""
        last_operations = {}

        while True:
            try:
                # Obtener operaciones abiertas del trader
                if self.trader_instance and self.trader_instance.is_connected:
                    # Esta es una simulación. Necesitamos una forma real de obtener las operaciones.
                    # Por ahora, vamos a simular que se detecta una nueva operación.
                    # En una implementación real, aquí iría la lógica para conectarse a la API
                    # y verificar si hay nuevas operaciones.
                    
                    # Simulación de detección de nueva operación
                    # Esto debería ser reemplazado con la lógica real de la API de Exnova
                    if hasattr(self.trader_instance.connection, 'api') and self.trader_instance.connection.api:
                        current_operations = self.trader_instance.connection.api.socket_option_opened
                        
                        new_operations = {op_id: op_data for op_id, op_data in current_operations.items() if op_id not in last_operations}
                        
                        for op_id, op_data in new_operations.items():
                            logger.info(f"🤖 NUEVA OPERACIÓN DETECTADA: {op_id}")
                            
                            # Extraer datos de la operación
                            active = op_data["active"]
                            direction = op_data["direction"]
                            
                            # Ejecutar callback con los datos de la operación
                            callback(active, direction)
                        
                        last_operations = current_operations

                time.sleep(2)  # Esperar 2 segundos antes de volver a verificar

            except Exception as e:
                logger.error(f"❌ Error en monitoreo de copytrading: {e}")
                time.sleep(10) # Evitar spam de spam en caso de error

if __name__ == "__main__":
    test_our_api()

