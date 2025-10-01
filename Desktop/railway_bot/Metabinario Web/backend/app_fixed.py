#!/usr/bin/env python3
"""
BOT DE COPYTRADING AUTOMÁTICO MULTI-USUARIO - VERSIÓN WEB CORREGIDA
Copytrading manual y automático 100% funcional con sistema multi-usuario
SIN DEPENDENCIAS DE TELEGRAM - SOLO WEB
VERSIÓN CORREGIDA PARA MANEJAR CONEXIONES PERSISTENTES
"""

import logging
import asyncio
import sys
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import time

# Importar nuestra propia API
from our_copytrading_api import OurCopyTradingAPI
from database import db_manager

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copytrading_web_fixed.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Base de datos simple para seguidores
DATABASE_FILE = "seguidores_database.json"
AUTHORIZED_USERS_FILE = "database/authorized_users.json"

# Variables globales del bot - UNA SOLA INSTANCIA GLOBAL
global_copytrading_api = None
user_sessions = {}

class AuthorizedUsersDatabase:
    """Manejo de base de datos de usuarios autorizados"""
    
    @staticmethod
    def load_database():
        """Cargar base de datos desde archivo"""
        if os.path.exists(AUTHORIZED_USERS_FILE):
            try:
                with open(AUTHORIZED_USERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"authorized_emails": [], "trader_email": "binariosector91@outlook.com"}
        return {"authorized_emails": [], "trader_email": "binariosector91@outlook.com"}
    
    @staticmethod
    def save_database(data):
        """Guardar base de datos en archivo"""
        try:
            os.makedirs(os.path.dirname(AUTHORIZED_USERS_FILE), exist_ok=True)
            with open(AUTHORIZED_USERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error guardando base de datos de usuarios autorizados: {e}")
            return False
    
    @staticmethod
    def is_trader(email):
        """Verificar si el email es del trader autorizado"""
        db = AuthorizedUsersDatabase.load_database()
        return email == db.get("trader_email", "binariosector91@outlook.com")
    
    @staticmethod
    def is_authorized(email):
        """Verificar si el email está autorizado"""
        db = AuthorizedUsersDatabase.load_database()
        return email in db.get("authorized_emails", [])
    
    @staticmethod
    def add_authorized_user(email):
        """Agregar usuario autorizado"""
        db = AuthorizedUsersDatabase.load_database()
        if email not in db["authorized_emails"]:
            db["authorized_emails"].append(email)
            return AuthorizedUsersDatabase.save_database(db)
        return False
    
    @staticmethod
    def remove_authorized_user(email):
        """Remover usuario autorizado"""
        db = AuthorizedUsersDatabase.load_database()
        if email in db["authorized_emails"]:
            db["authorized_emails"].remove(email)
            return AuthorizedUsersDatabase.save_database(db)
        return False
    
    @staticmethod
    def get_authorized_users():
        """Obtener lista de usuarios autorizados"""
        db = AuthorizedUsersDatabase.load_database()
        return db.get("authorized_emails", [])

class FollowerDatabase:
    """Manejo de base de datos simple para seguidores"""
    
    @staticmethod
    def load_database():
        """Cargar base de datos desde archivo"""
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"followers": []}
        return {"followers": []}
    
    @staticmethod
    def save_database(data):
        """Guardar base de datos en archivo"""
        try:
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error guardando base de datos: {e}")
            return False
    
    @staticmethod
    def register_follower(user_id, username, email, password, balance_mode, amount):
        """Registrar o actualizar seguidor"""
        db = FollowerDatabase.load_database()
        
        # Verificar si ya existe un seguidor con el mismo user_id o email
        existing_follower_index = -1
        for i, follower in enumerate(db["followers"]):
            if follower["user_id"] == user_id or follower["email"] == email:
                existing_follower_index = i
                break

        if existing_follower_index != -1:
            # Actualizar existente
            db["followers"][existing_follower_index].update({
                "username": username,
                "email": email,
                "password": password,
                "balance_mode": balance_mode,
                "amount": amount,
                "updated_at": datetime.now().isoformat(),
                "active": True
            })
            logger.info(f"✅ Seguidor {email} (ID: {user_id}) actualizado en la base de datos.")
        else:
            # Agregar nuevo
            db["followers"].append({
                "user_id": user_id,
                "username": username,
                "email": email,
                "password": password,
                "balance_mode": balance_mode,
                "amount": amount,
                "added_at": datetime.now().isoformat(),
                "active": True
            })
            logger.info(f"✅ Nuevo seguidor {email} (ID: {user_id}) agregado a la base de datos.")
        
        return FollowerDatabase.save_database(db)
    
    @staticmethod
    def get_followers():
        """Obtener lista de seguidores activos"""
        db = FollowerDatabase.load_database()
        return [follower for follower in db["followers"] if follower.get("active", True)]
    
    @staticmethod
    def update_follower_amount(email, new_amount):
        """Actualizar importe del seguidor por email"""
        db = FollowerDatabase.load_database()
        for follower in db["followers"]:
            if follower["email"] == email:
                follower["amount"] = new_amount
                follower["updated_at"] = datetime.now().isoformat()
                FollowerDatabase.save_database(db)
                logger.info(f"✅ Importe del seguidor {email} actualizado a ${new_amount}.")
                return True
        logger.warning(f"⚠️ No se encontró seguidor con email {email} para actualizar importe.")
        return False

class WebBotSession:
    """Sesión del bot web para cada usuario"""
    
    def __init__(self, user_id, username="", email="", role="follower"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.current_step = None
        self.is_connected = False
        
        logger.info(f"🔧 Nueva sesión web creada para {email} ({role})")

def get_global_api():
    """Obtener la instancia global de la API"""
    global global_copytrading_api
    if global_copytrading_api is None:
        global_copytrading_api = OurCopyTradingAPI()
        logger.info("🔧 Instancia global de API creada")
    return global_copytrading_api

def get_or_create_session(user_id, username="", email="", role="follower"):
    """Obtener o crear sesión para usuario"""
    if user_id not in user_sessions:
        user_sessions[user_id] = WebBotSession(user_id, username, email, role)
    else:
        # Actualizar email si se proporciona
        if email and hasattr(user_sessions[user_id], 'email'):
            user_sessions[user_id].email = email
    return user_sessions[user_id]

def send_web_notification(user_id, notification_type, data):
    """Enviar notificación via WebSocket"""
    try:
        socketio.emit(notification_type, data, room=user_id)
        logger.info(f"📡 Notificación enviada a {user_id}: {notification_type}")
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")

def notify_all_followers(notification_type, message):
    """Notificar a todos los seguidores"""
    try:
        followers = FollowerDatabase.get_followers()
        for follower in followers:
            user_id = follower["user_id"]
            send_web_notification(user_id, notification_type, {
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
        logger.info(f"📢 Notificación enviada a {len(followers)} seguidores")
    except Exception as e:
        logger.error(f"Error notificando seguidores: {e}")

# Crear aplicación Flask
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = 'metabinario_web_secret_key'

# Configurar CORS para permitir peticiones desde el navegador
CORS(app, origins=["http://127.0.0.1:5004", "http://localhost:5004"], supports_credentials=True)

socketio = SocketIO(app, cors_allowed_origins="*")

# Ruta para servir el frontend
@app.route('/')
def serve_frontend():
    """Servir el frontend"""
    return app.send_static_file('index.html')

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/login', methods=['POST'])
def web_login():
    """Login de usuario web - VERSIÓN CORREGIDA CON AUTORIZACIÓN"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'follower')
        balance_mode = data.get('balance_mode', 'PRACTICE')
        amount = data.get('amount', 10.0)
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        # Verificar autorización según el rol
        if role == "trader":
            if not AuthorizedUsersDatabase.is_trader(email):
                return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede acceder al panel de trader.'}), 403
        elif role == "follower":
            if not AuthorizedUsersDatabase.is_authorized(email):
                return jsonify({'error': 'Acceso denegado. Tu email no está autorizado para usar este bot. Contacta al trader para obtener acceso.'}), 403
        
        # Crear ID único para el usuario
        user_id = f"{email}_{role}"
        
        # Obtener o crear sesión
        session_obj = get_or_create_session(user_id, email, email, role)
        session_obj.email = email
        
        # Usar la instancia global de la API
        api = get_global_api()
        
        # Intentar conectar con ExNova según el rol
        success = False
        
        if role == 'trader':
            success = api.add_trader_account(email, password, balance_mode)
            if success:
                send_web_notification(user_id, 'trader_connected', {
                    'email': email,
                    'connected': True,
                    'balance_mode': balance_mode
                })
        else:  # follower
            success = api.add_follower_account(email, password, balance_mode)
            if success:
                # Registrar en base de datos
                FollowerDatabase.register_follower(
                    user_id, email, email, password, balance_mode, amount
                )
                send_web_notification(user_id, 'follower_connected', {
                    'email': email,
                    'connected': True,
                    'balance_mode': balance_mode,
                    'amount': amount
                })
        
        if success:
            session['user_id'] = user_id
            return jsonify({
                'success': True,
                'user_id': user_id,
                'user': {
                    'email': email,
                    'role': role,
                    'exnova_connected': True
                }
            })
        else:
            return jsonify({'error': 'Error conectando con ExNova. Verifica las credenciales.'}), 400
            
    except Exception as e:
        logger.error(f"Error en login web: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE TRADER ====================

@app.route('/api/trader/status', methods=['GET'])
def get_trader_status():
    """Obtener estado del trader"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        api = get_global_api()
        status = api.get_status()
        
        return jsonify({
            'success': True,
            'trader_status': status.get('trader', {}),
            'followers_count': len(status.get('followers', [])),
            'auto_copy_active': api.is_auto_copy_active()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del trader: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/trader/stop-auto-copy', methods=['POST'])
def stop_auto_copytrading():
    """Detener copytrading automático - VERSIÓN CORREGIDA"""
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        api = get_global_api()
        
        # Detener el copytrading automático
        if api.is_auto_copy_active():
            api.auto_copy_active = False
            
            # Detener monitoreo en el trader
            if api.trader_instance:
                api.trader_instance.stop_monitoring()
            
            # Notificar a todos los seguidores
            notify_all_followers("auto_copy_stopped", "🛑 COPYTRADING AUTOMÁTICO DETENIDO\n\nEl Metabinario Trader ha detenido el copytrading automático.")
            
            return jsonify({
                'success': True,
                'message': 'COPYTRADING AUTOMÁTICO DETENIDO'
            })
        else:
            return jsonify({
                'error': 'El copytrading automático no está activo'
            }), 400
            
    except Exception as e:
        logger.error(f"Error deteniendo copytrading automático: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/trader/start-auto-copy', methods=['POST'])
def start_auto_copytrading():
    """Activar copytrading automático - VERSIÓN CORREGIDA"""
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        api = get_global_api()
        status = api.get_status()
        
        # Verificar que hay trader configurado
        if not status['trader']:
            return jsonify({
                'error': 'No hay cuenta trader configurada. Primero configura la cuenta trader para usar el copytrading automático.'
            }), 400
        
        # Obtener seguidores de la base de datos y agregarlos a la API
        followers = FollowerDatabase.get_followers()
        
        if len(followers) == 0:
            return jsonify({
                'error': 'No hay seguidores registrados en el sistema.'
            }), 400
        
        # Agregar seguidores a la API si no están ya agregados
        for follower in followers:
            # Verificar si el seguidor ya está conectado
            follower_connected = False
            for existing_follower in api.follower_instances:
                if existing_follower.email == follower['email']:
                    follower_connected = True
                    break
            
            if not follower_connected:
                api.add_follower_account(
                    follower['email'],
                    follower['password'],
                    follower['balance_mode']
                )

        # Función de callback para replicar operaciones
        def replicate_operation_callback(active, direction):
            """Callback para replicar operaciones en todos los seguidores"""
            try:
                logger.info(f"🤖 [CALLBACK] Replicando operación: {active} {direction}")
                
                # Replicar en todos los seguidores con bot encendido
                for follower in api.follower_instances:
                    if api.get_follower_bot_status(follower.email):
                        try:
                            # Obtener importe configurado del seguidor desde la base de datos actualizada
                            try:
                                import json
                                import os
                                
                                # Buscar el archivo de base de datos
                                db_path = "seguidores_database.json"
                                follower_amount = 10.0  # Importe por defecto
                                
                                if os.path.exists(db_path):
                                    with open(db_path, 'r', encoding='utf-8') as f:
                                        db_data = json.load(f)
                                        followers_db = db_data.get("followers", [])
                                        
                                        # Buscar el seguidor por email
                                        for f in followers_db:
                                            if f.get("email") == follower.email:
                                                follower_amount = float(f.get("amount", 10.0))
                                                logger.info(f"💰 Usando importe configurado del seguidor: ${follower_amount}")
                                                break
                                        else:
                                            # Fallback: buscar en la lista de seguidores
                                            for f in followers:
                                                if f['email'] == follower.email:
                                                    follower_amount = float(f['amount'])
                                                    break
                                            logger.info(f"💰 Usando importe de lista de seguidores: ${follower_amount}")
                                else:
                                    # Fallback: buscar en la lista de seguidores
                                    follower_amount = 10.0  # Importe por defecto
                                    for f in followers:
                                        if f['email'] == follower.email:
                                            follower_amount = float(f['amount'])
                                            break
                                    logger.info(f"💰 Usando importe de lista de seguidores: ${follower_amount}")
                                    
                            except Exception as e:
                                follower_amount = 10.0  # Importe por defecto en caso de error
                                logger.warning(f"⚠️ Error obteniendo importe del seguidor, usando por defecto: ${follower_amount} - Error: {e}")
                            
                            # Convertir formato de divisa
                            from our_copytrading_api import convert_currency_format
                            converted_active = convert_currency_format(active)
                            
                            # Ejecutar operación
                            success, result = follower.execute_operation(
                                follower_amount,
                                converted_active,
                                direction,
                                2  # Duración por defecto
                            )
                            
                            if success:
                                logger.info(f"✅ [CALLBACK] Operación exitosa en {follower.email}: {result}")
                            else:
                                logger.error(f"❌ [CALLBACK] Error en {follower.email}: {result}")
                                
                        except Exception as e:
                            logger.error(f"❌ [CALLBACK] Error replicando en {follower.email}: {e}")
                    else:
                        logger.info(f"⏸️ [CALLBACK] Seguidor {follower.email} con bot APAGADO")
                        
            except Exception as e:
                logger.error(f"❌ [CALLBACK] Error en callback: {e}")

        # Iniciar monitoreo de copytrading automático
        success = api.start_auto_copy_monitoring_old(
            trader_email=email,
            follower_instances=api.follower_instances,
            auto_copy_amount=10.0,
            context="web_bot",
            user_id=f"{email}_trader"
        )
        
        if success:
            # Notificar a todos los seguidores
            notify_all_followers("auto_copy_activated", "🤖 COPYTRADING AUTOMÁTICO ACTIVADO\n\nEl Metabinario Trader ha activado el copytrading automático. Recibirás sus operaciones automáticamente con tu importe configurado.")
            
            return jsonify({
                'success': True,
                'message': 'COPYTRADING AUTOMÁTICO ACTIVADO',
                'trader_email': status['trader']['email'],
                'followers_count': len(followers),
                'followers': [
                    {
                        'email': f['email'],
                        'amount': f['amount']
                    } for f in followers
                ]
            })
        else:
            return jsonify({
                'error': 'Error iniciando copytrading automático. Verifica que las cuentas estén conectadas correctamente.'
            }), 500
            
    except Exception as e:
        logger.error(f"Error iniciando copytrading automático: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE ADMINISTRACIÓN DE USUARIOS ====================

@app.route('/api/admin/authorized-users', methods=['GET'])
def get_authorized_users():
    """Obtener lista de usuarios autorizados - Solo para trader"""
    try:
        data = request.get_json() if request.is_json else {}
        email = data.get('email') or request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        # Verificar que sea el trader autorizado
        if not AuthorizedUsersDatabase.is_trader(email):
            return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede acceder a esta función.'}), 403
        
        authorized_users = AuthorizedUsersDatabase.get_authorized_users()
        trader_email = AuthorizedUsersDatabase.load_database().get("trader_email", "binariosector91@outlook.com")
        
        return jsonify({
            'success': True,
            'authorized_users': authorized_users,
            'trader_email': trader_email,
            'total_authorized': len(authorized_users)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios autorizados: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/admin/add-user', methods=['POST'])
def add_authorized_user():
    """Agregar usuario autorizado - Solo para trader"""
    try:
        data = request.get_json()
        email = data.get('email')
        trader_email = data.get('trader_email')
        
        if not email or not trader_email:
            return jsonify({'error': 'Email y trader_email requeridos'}), 400
        
        # Verificar que sea el trader autorizado
        if not AuthorizedUsersDatabase.is_trader(trader_email):
            return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede agregar usuarios.'}), 403
        
        if AuthorizedUsersDatabase.add_authorized_user(email):
            logger.info(f"✅ Usuario autorizado agregado: {email} por trader: {trader_email}")
            return jsonify({
                'success': True,
                'message': f'Usuario {email} agregado exitosamente a la lista de autorizados'
            })
        else:
            return jsonify({'error': 'El usuario ya está autorizado'}), 400
            
    except Exception as e:
        logger.error(f"Error agregando usuario autorizado: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/admin/remove-user', methods=['POST'])
def remove_authorized_user():
    """Remover usuario autorizado - Solo para trader"""
    try:
        data = request.get_json()
        email = data.get('email')
        trader_email = data.get('trader_email')
        
        if not email or not trader_email:
            return jsonify({'error': 'Email y trader_email requeridos'}), 400
        
        # Verificar que sea el trader autorizado
        if not AuthorizedUsersDatabase.is_trader(trader_email):
            return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede remover usuarios.'}), 403
        
        if AuthorizedUsersDatabase.remove_authorized_user(email):
            logger.info(f"✅ Usuario autorizado removido: {email} por trader: {trader_email}")
            return jsonify({
                'success': True,
                'message': f'Usuario {email} removido exitosamente de la lista de autorizados'
            })
        else:
            return jsonify({'error': 'El usuario no está autorizado'}), 400
            
    except Exception as e:
        logger.error(f"Error removiendo usuario autorizado: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE SEGUIDORES ====================

@app.route('/api/follower/register', methods=['POST'])
def register_follower():
    """Registrar seguidor"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        balance_mode = data.get('balance_mode', 'PRACTICE')
        amount = data.get('amount', 10.0)
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        user_id = f"{email}_follower"
        
        # Registrar en base de datos
        success = FollowerDatabase.register_follower(
            user_id, email, email, password, balance_mode, amount
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Seguidor registrado exitosamente',
                'user_id': user_id
            })
        else:
            return jsonify({'error': 'Error registrando seguidor'}), 500
            
    except Exception as e:
        logger.error(f"Error registrando seguidor: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE CONTROL DE BOT SEGUIDOR ====================

@app.route('/api/follower/start-bot', methods=['POST'])
def start_follower_bot():
    """Encender bot del seguidor"""
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        api = get_global_api()
        success = api.start_follower_bot(email)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Bot del seguidor encendido exitosamente'
            })
        else:
            return jsonify({'error': 'Error encendiendo bot del seguidor'}), 500
            
    except Exception as e:
        logger.error(f"Error encendiendo bot del seguidor: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/follower/stop-bot', methods=['POST'])
def stop_follower_bot():
    """Apagar bot del seguidor"""
    try:
        data = request.get_json()
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        api = get_global_api()
        success = api.stop_follower_bot(email)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Bot del seguidor apagado exitosamente'
            })
        else:
            return jsonify({'error': 'Error apagando bot del seguidor'}), 500
            
    except Exception as e:
        logger.error(f"Error apagando bot del seguidor: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/follower/bot-status', methods=['GET'])
def get_follower_bot_status():
    """Obtener estado del bot del seguidor"""
    try:
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email requerido como parámetro'}), 400
        
        api = get_global_api()
        bot_status = api.get_follower_bot_status(email)
        
        return jsonify({
            'success': True,
            'bot_status': bot_status
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del bot: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/follower/update-amount', methods=['POST'])
def update_follower_amount():
    """Actualizar importe del seguidor"""
    try:
        data = request.get_json()
        email = data.get('email')
        new_amount = data.get('amount', 10.0)
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        # Actualizar en la base de datos
        success = FollowerDatabase.update_follower_amount(email, new_amount)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Importe actualizado a ${new_amount}'
            })
        else:
            return jsonify({'error': 'Error actualizando importe'}), 500
            
    except Exception as e:
        logger.error(f"Error actualizando importe: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/copytrading/manual', methods=['POST'])
def execute_manual_copytrading():
    """Ejecutar copytrading manual"""
    try:
        data = request.get_json()
        amount = data.get('amount', 10.0)
        active = data.get('active', 'EURUSD-OTC')
        direction = data.get('direction', 'CALL')
        duration = data.get('duration', 2)
        
        api = get_global_api()
        
        # Ejecutar copytrading manual
        results = api.execute_copytrading_operation(
            amount=amount,
            active=active,
            direction=direction,
            duration=duration
        )
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logger.error(f"Error en copytrading manual: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE ESTADO ====================

@app.route('/api/status', methods=['GET'])
def get_system_status():
    """Obtener estado del sistema"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        api = get_global_api()
        status = api.get_status()
        
        return jsonify({
            'success': True,
            'system_status': status,
            'auto_copy_active': api.is_auto_copy_active(),
            'followers_count': len(FollowerDatabase.get_followers())
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Manejar conexión WebSocket"""
    logger.info(f"🔌 Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Manejar desconexión WebSocket"""
    logger.info(f"🔌 Cliente desconectado: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    """Unirse a una sala específica"""
    room = data.get('room')
    if room:
        socketio.emit('joined_room', {'room': room}, room=request.sid)
        logger.info(f"🔌 Cliente {request.sid} se unió a la sala {room}")

if __name__ == '__main__':
    logger.info("🚀 Iniciando Metabinario Web Bot CORREGIDO...")
    logger.info("📊 Sistema de Copytrading Web - VERSIÓN FIXED")
    logger.info("🌐 Sin dependencias de Telegram")
    logger.info("🔗 API REST + WebSocket")
    logger.info("🔧 Conexiones persistentes habilitadas")
    
    # Crear directorio de base de datos si no existe
    os.makedirs("database", exist_ok=True)
    
    socketio.run(app, host='0.0.0.0', port=5004, debug=False, allow_unsafe_werkzeug=True)
