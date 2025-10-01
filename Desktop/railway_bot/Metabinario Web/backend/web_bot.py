#!/usr/bin/env python3
"""
BOT DE COPYTRADING AUTOMÁTICO MULTI-USUARIO - VERSIÓN WEB
Copytrading manual y automático 100% funcional con sistema multi-usuario
SIN DEPENDENCIAS DE TELEGRAM - SOLO WEB
"""

import logging
import asyncio
import sys
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit
import threading
import time

# Importar nuestra propia API
from our_copytrading_api import OurCopyTradingAPI

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('copytrading_web.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Base de datos simple para seguidores
DATABASE_FILE = "seguidores_database.json"

# Variables globales del bot
user_sessions = {}

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
    def update_follower_amount(user_id, new_amount):
        """Actualizar importe del seguidor"""
        db = FollowerDatabase.load_database()
        for follower in db["followers"]:
            if follower["user_id"] == user_id:
                follower["amount"] = new_amount
                follower["updated_at"] = datetime.now().isoformat()
                FollowerDatabase.save_database(db)
                logger.info(f"✅ Importe del seguidor {user_id} actualizado a ${new_amount}.")
                return True
        return False

class WebBotSession:
    """Sesión del bot web para cada usuario"""
    
    def __init__(self, user_id, username="", email="", role="follower"):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.role = role
        self.current_step = None
        self.copytrading_api = OurCopyTradingAPI()
        self.is_connected = False
        
        logger.info(f"🔧 Nueva sesión web creada para {email} ({role})")

def get_or_create_session(user_id, username="", email="", role="follower"):
    """Obtener o crear sesión para usuario"""
    if user_id not in user_sessions:
        user_sessions[user_id] = WebBotSession(user_id, username, email, role)
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
app = Flask(__name__)
app.config['SECRET_KEY'] = 'metabinario_web_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/login', methods=['POST'])
def web_login():
    """Login de usuario web - FUNCIÓN ORIGINAL ADAPTADA"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'follower')
        balance_mode = data.get('balance_mode', 'PRACTICE')
        amount = data.get('amount', 10.0)
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        # Crear ID único para el usuario
        user_id = f"{email}_{role}"
        
        # Obtener o crear sesión
        session_obj = get_or_create_session(user_id, email, email, role)
        
        # Intentar conectar con ExNova según el rol
        success = False
        
        if role == 'trader':
            success = session_obj.copytrading_api.add_trader_account(email, password, balance_mode)
            if success:
                send_web_notification(user_id, 'trader_connected', {
                    'email': email,
                    'connected': True,
                    'balance_mode': balance_mode
                })
        else:  # follower
            success = session_obj.copytrading_api.add_follower_account(email, password, balance_mode)
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
            return jsonify({'error': 'Error conectando con ExNova'}), 400
            
    except Exception as e:
        logger.error(f"Error en login web: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE TRADER ====================

@app.route('/api/trader/status', methods=['GET'])
def get_trader_status():
    """Obtener estado del trader - FUNCIÓN ORIGINAL ADAPTADA"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        session_obj = get_or_create_session(user_id)
        status = session_obj.copytrading_api.get_status()
        
        return jsonify({
            'success': True,
            'trader_status': status.get('trader', {}),
            'followers_count': len(status.get('followers', [])),
            'auto_copy_active': session_obj.copytrading_api.is_auto_copy_active()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado del trader: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/trader/start-auto-copy', methods=['POST'])
def start_auto_copytrading():
    """Activar copytrading automático - FUNCIÓN ORIGINAL ADAPTADA"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        session_obj = get_or_create_session(user_id)
        status = session_obj.copytrading_api.get_status()
        
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
        
        # Agregar seguidores a la API original
        for follower in followers:
            session_obj.copytrading_api.add_follower_account(
                follower['email'],
                follower['password'],
                follower['balance_mode']
            )

        # Activar copytrading automático directamente sin pedir importe
        session_obj.current_step = "auto_copy_active"
        
        # Iniciar monitoreo de copytrading automático (cada seguidor usa su importe individual)
        success = session_obj.copytrading_api.start_auto_copy_monitoring(
            status['trader']['email'],
            session_obj.copytrading_api.follower_instances,
            10,  # Importe dummy - cada seguidor usa su propio importe configurado
            None,  # context
            user_id
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

@app.route('/api/trader/stop-auto-copy', methods=['POST'])
def stop_auto_copytrading():
    """Detener copytrading automático - FUNCIÓN ORIGINAL ADAPTADA"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        session_obj = get_or_create_session(user_id)
        
        if session_obj.copytrading_api.is_auto_copy_active():
            session_obj.copytrading_api.stop_auto_copy_monitoring()
            
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

# ==================== RUTAS DE SEGUIDORES ====================

@app.route('/api/follower/register', methods=['POST'])
def register_follower():
    """Registrar seguidor - FUNCIÓN ORIGINAL ADAPTADA"""
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

@app.route('/api/follower/update-amount', methods=['POST'])
def update_follower_amount():
    """Actualizar importe del seguidor - FUNCIÓN ORIGINAL ADAPTADA"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        data = request.get_json()
        new_amount = data.get('amount', 10.0)
        
        success = FollowerDatabase.update_follower_amount(user_id, new_amount)
        
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

# ==================== RUTAS DE COPYTRADING MANUAL ====================

@app.route('/api/copytrading/manual', methods=['POST'])
def execute_manual_copytrading():
    """Ejecutar copytrading manual - FUNCIÓN ORIGINAL ADAPTADA"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'No autorizado'}), 401
        
        data = request.get_json()
        amount = data.get('amount', 10.0)
        active = data.get('active', 'EURUSD-OTC')
        direction = data.get('direction', 'CALL')
        duration = data.get('duration', 2)
        
        session_obj = get_or_create_session(user_id)
        
        # Ejecutar copytrading manual
        results = session_obj.copytrading_api.execute_copytrading_operation(
            amount=amount,
            active=active,
            direction=direction,
            duration=duration
        )
        
        # Enviar notificación via WebSocket
        socketio.emit('copytrading_result', {
            'type': 'manual',
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, room=user_id)
        
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
        
        session_obj = get_or_create_session(user_id)
        status = session_obj.copytrading_api.get_status()
        
        return jsonify({
            'success': True,
            'system_status': status,
            'auto_copy_active': session_obj.copytrading_api.is_auto_copy_active(),
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
    logger.info("🚀 Iniciando Metabinario Web Bot...")
    logger.info("📊 Sistema de Copytrading Web")
    logger.info("🌐 Sin dependencias de Telegram")
    logger.info("🔗 API REST + WebSocket")
    
    # Crear directorio de base de datos si no existe
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
