#!/usr/bin/env python3
"""
Bot de Trading Web - Versión para Railway
"""

import os
import sys
import json
import logging
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import threading
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
CORS(app)

# Inicializar SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Base de datos simple
DATABASE_FILE = "database/authorized_users.json"
FOLLOWERS_FILE = "database/followers.json"

def ensure_directories():
    """Crear directorios necesarios"""
    os.makedirs("database", exist_ok=True)
    os.makedirs("frontend", exist_ok=True)

def load_database():
    """Cargar base de datos de usuarios autorizados"""
    try:
        with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"authorized_emails": [], "trader_email": "binariosector91@outlook.com"}

def save_database(data):
    """Guardar base de datos"""
    with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def load_followers():
    """Cargar base de datos de seguidores"""
    try:
        with open(FOLLOWERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"followers": []}

def save_followers(data):
    """Guardar base de datos de seguidores"""
    with open(FOLLOWERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Variables globales
user_sessions = {}
bot_running = False

# ==================== RUTAS WEB ====================

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/status')
def status():
    """Estado del bot"""
    return jsonify({
        'status': 'online',
        'message': 'Bot funcionando correctamente',
        'version': '1.0.0',
        'users_online': len(user_sessions)
    })

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not email or not password or not role:
            return jsonify({'error': 'Email, contraseña y rol requeridos'}), 400
        
        # Verificar autorización según el rol
        db = load_database()
        if role == "trader":
            if email != db.get("trader_email", "binariosector91@outlook.com"):
                return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede acceder al panel de trader.'}), 403
        elif role == "follower":
            if email not in db.get("authorized_emails", []):
                return jsonify({'error': 'Acceso denegado. Tu email no está autorizado para usar este bot. Contacta al trader para obtener acceso.'}), 403
        
        # Crear sesión
        user_id = f"{email}_{role}"
        user_sessions[user_id] = {
            'email': email,
            'role': role,
            'connected_at': time.time()
        }
        
        logger.info(f"✅ Usuario {email} ({role}) inició sesión")
        
        return jsonify({
            'success': True,
            'message': 'Login exitoso',
            'user_id': user_id,
            'role': role
        })
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# ==================== RUTAS DE ADMINISTRACIÓN ====================

@app.route('/api/admin/authorized-users', methods=['GET'])
def get_authorized_users():
    """Obtener lista de usuarios autorizados - Solo para trader"""
    try:
        data = request.get_json() if request.is_json else {}
        email = data.get('email') or request.args.get('email')
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        # Verificar que sea el trader autorizado
        db = load_database()
        if email != db.get("trader_email", "binariosector91@outlook.com"):
            return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede acceder a esta función.'}), 403
        
        return jsonify({
            'success': True,
            'authorized_users': db.get("authorized_emails", []),
            'trader_email': db.get("trader_email", "binariosector91@outlook.com"),
            'total_authorized': len(db.get("authorized_emails", []))
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
        db = load_database()
        if trader_email != db.get("trader_email", "binariosector91@outlook.com"):
            return jsonify({'error': 'Acceso denegado. Solo el trader autorizado puede agregar usuarios.'}), 403
        
        if email not in db["authorized_emails"]:
            db["authorized_emails"].append(email)
            save_database(db)
            logger.info(f"✅ Usuario autorizado agregado: {email} por trader: {trader_email}")
            return jsonify({
                'success': True,
                'message': f'Usuario {email} agregado exitosamente a la lista de autorizados'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Usuario {email} ya está en la lista de autorizados'
            })
        
    except Exception as e:
        logger.error(f"Error agregando usuario autorizado: {e}")
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
    """Unirse a una sala"""
    room = data.get('room', 'general')
    join_room(room)
    logger.info(f"🔌 Cliente {request.sid} se unió a la sala {room}")

@socketio.on('trader_operation')
def handle_trader_operation(data):
    """Manejar operación del trader"""
    try:
        # Emitir a todos los seguidores
        emit('new_operation', data, room='followers', include_self=False)
        logger.info(f"📊 Operación del trader emitida: {data}")
    except Exception as e:
        logger.error(f"Error manejando operación del trader: {e}")

# ==================== FUNCIONES DE INICIO ====================

def initialize_database():
    """Inicializar base de datos si no existe"""
    ensure_directories()
    
    # Crear base de datos de usuarios autorizados
    if not os.path.exists(DATABASE_FILE):
        initial_data = {
            "authorized_emails": ["clickrealbinarias@outlook.com"],
            "trader_email": "binariosector91@outlook.com"
        }
        save_database(initial_data)
        logger.info("✅ Base de datos de usuarios autorizados creada")
    
    # Crear base de datos de seguidores
    if not os.path.exists(FOLLOWERS_FILE):
        initial_followers = {"followers": []}
        save_followers(initial_followers)
        logger.info("✅ Base de datos de seguidores creada")

if __name__ == '__main__':
    # Inicializar base de datos
    initialize_database()
    
    # Obtener puerto de Railway
    port = int(os.environ.get('PORT', 5000))
    
    logger.info("🚀 Iniciando Bot de Trading Web...")
    logger.info("📊 Sistema de Copytrading Web")
    logger.info("🌐 Versión para Railway")
    logger.info(f"🔗 Puerto: {port}")
    
    # Iniciar servidor
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
