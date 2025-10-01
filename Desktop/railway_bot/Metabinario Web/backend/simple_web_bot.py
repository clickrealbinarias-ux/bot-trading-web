#!/usr/bin/env python3
"""
BOT DE COPYTRADING WEB SIMPLIFICADO
Versión simplificada que usa conexiones directas sin procesos independientes
"""

import logging
import sys
import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit

# Agregar exnovaapi al path
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi')

from exnovaapi.stable_api import Exnova
import exnovaapi.global_value as global_value

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('simple_web_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Variables globales
trader_connection = None
follower_connections = {}
follower_bot_status = {}
auto_copy_active = False
monitoring_thread = None

def convert_currency_format(currency: str) -> str:
    """Convertir formato de divisa para mercado real"""
    real_market_mapping = {
        'EURUSD': 'EURUSD-op',
        'GBPUSD': 'GBPUSD-op',
        'USDJPY': 'USDJPY-op',
        'EURJPY': 'EURJPY-op',
        'AUDUSD': 'AUDUSD-op',
        'USDCAD': 'USDCAD-op',
        'NZDUSD': 'NZDUSD-op',
        'EURGBP': 'EURGBP-op',
        'EURAUD': 'EURAUD-op',
        'GBPJPY': 'GBPJPY-op',
        'AUDJPY': 'AUDJPY-op',
        'CADJPY': 'CADJPY-op',
        'NZDJPY': 'NZDJPY-op',
        'GBPAUD': 'GBPAUD-op',
        'GBPCAD': 'GBPCAD-op',
        'AUDCAD': 'AUDCAD-op',
        'AUDNZD': 'AUDNZD-op',
        'NZDCAD': 'NZDCAD-op',
        'USDCHF': 'USDCHF-op',
        'EURCHF': 'EURCHF-op',
        'GBPCHF': 'GBPCHF-op',
        'AUDCHF': 'AUDCHF-op',
        'NZDCHF': 'NZDCHF-op',
        'CHFJPY': 'CHFJPY-op'
    }
    
    if currency.endswith('-OTC') or currency.endswith('-op'):
        return currency
    
    if currency in real_market_mapping:
        return real_market_mapping[currency]
    
    return currency

def connect_trader(email, password, balance_mode):
    """Conectar cuenta trader"""
    global trader_connection
    
    try:
        logger.info(f"🔗 Conectando trader: {email}")
        connection = Exnova(email, password)
        connection.connect()
        
        if hasattr(connection, 'api') and connection.api:
            connection.change_balance(balance_mode)
            trader_connection = connection
            logger.info(f"✅ Trader conectado: {email}")
            return True
        else:
            logger.error(f"❌ Error conectando trader: {email}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error conectando trader: {e}")
        return False

def connect_follower(email, password, balance_mode):
    """Conectar cuenta seguidor"""
    global follower_connections, follower_bot_status
    
    try:
        logger.info(f"🔗 Conectando seguidor: {email}")
        connection = Exnova(email, password)
        connection.connect()
        
        if hasattr(connection, 'api') and connection.api:
            connection.change_balance(balance_mode)
            follower_connections[email] = connection
            follower_bot_status[email] = False  # Bot apagado por defecto
            logger.info(f"✅ Seguidor conectado: {email}")
            return True
        else:
            logger.error(f"❌ Error conectando seguidor: {email}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error conectando seguidor: {e}")
        return False

def start_follower_bot(email):
    """Encender bot del seguidor"""
    global follower_bot_status
    
    if email in follower_connections:
        follower_bot_status[email] = True
        logger.info(f"🤖 Bot del seguidor ENCENDIDO: {email}")
        return True
    else:
        logger.warning(f"⚠️ Seguidor no conectado: {email}")
        return False

def stop_follower_bot(email):
    """Apagar bot del seguidor"""
    global follower_bot_status
    
    if email in follower_connections:
        follower_bot_status[email] = False
        logger.info(f"🛑 Bot del seguidor APAGADO: {email}")
        return True
    else:
        logger.warning(f"⚠️ Seguidor no conectado: {email}")
        return False

def get_follower_bot_status(email):
    """Obtener estado del bot del seguidor"""
    return follower_bot_status.get(email, False)

def replicate_operation_callback(active, direction):
    """Callback para replicar operaciones en seguidores"""
    global follower_connections, follower_bot_status
    
    try:
        logger.info(f"🤖 [CALLBACK] Replicando operación: {active} {direction}")
        
        # Replicar en todos los seguidores con bot encendido
        for email, connection in follower_connections.items():
            if get_follower_bot_status(email):
                try:
                    # Convertir formato de divisa
                    converted_active = convert_currency_format(active)
                    
                    # Ejecutar operación
                    success, result = connection.buy(10.0, converted_active, direction, 2)
                    
                    if success:
                        logger.info(f"✅ [CALLBACK] Operación exitosa en {email}: {result}")
                    else:
                        logger.error(f"❌ [CALLBACK] Error en {email}: {result}")
                        
                except Exception as e:
                    logger.error(f"❌ [CALLBACK] Error replicando en {email}: {e}")
            else:
                logger.info(f"⏸️ [CALLBACK] Seguidor {email} con bot APAGADO")
                
    except Exception as e:
        logger.error(f"❌ [CALLBACK] Error en callback: {e}")

def monitor_trader_operations():
    """Monitorear operaciones del trader"""
    global trader_connection, auto_copy_active
    
    last_operations = {}
    
    while auto_copy_active:
        try:
            if trader_connection and hasattr(trader_connection, 'api') and trader_connection.api:
                current_operations = getattr(trader_connection.api, 'socket_option_opened', {})
                
                # Detectar nuevas operaciones
                new_operations = {op_id: op_data for op_id, op_data in current_operations.items() if op_id not in last_operations}
                
                for op_id, op_data in new_operations.items():
                    logger.info(f"🤖 NUEVA OPERACIÓN DETECTADA: {op_id}")
                    
                    # Extraer datos de la operación
                    msg_data = op_data.get('msg', {})
                    active = msg_data.get('active', '')
                    direction = msg_data.get('dir', '')
                    
                    # Llamar al callback
                    if active and direction:
                        replicate_operation_callback(active, direction)
                
                last_operations = current_operations.copy()
            
            time.sleep(2)  # Esperar 2 segundos
            
        except Exception as e:
            logger.error(f"❌ Error en monitoreo: {e}")
            time.sleep(10)

def start_auto_copy_monitoring():
    """Iniciar monitoreo de copytrading automático"""
    global auto_copy_active, monitoring_thread
    
    if not trader_connection:
        logger.error("❌ No hay trader conectado")
        return False
    
    auto_copy_active = True
    monitoring_thread = threading.Thread(target=monitor_trader_operations)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    
    logger.info("🤖 Monitoreo de copytrading automático iniciado")
    return True

def stop_auto_copy_monitoring():
    """Detener monitoreo de copytrading automático"""
    global auto_copy_active
    auto_copy_active = False
    logger.info("🛑 Monitoreo de copytrading automático detenido")

# Crear aplicación Flask
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = 'metabinario_web_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Ruta para servir el frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

# API Routes
@app.route('/api/login', methods=['POST'])
def web_login():
    """Login de usuario"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'follower')
        balance_mode = data.get('balance_mode', 'PRACTICE')
        
        if not email or not password:
            return jsonify({'error': 'Email y contraseña requeridos'}), 400
        
        success = False
        
        if role == 'trader':
            success = connect_trader(email, password, balance_mode)
        else:
            success = connect_follower(email, password, balance_mode)
        
        if success:
            session['user_id'] = f"{email}_{role}"
            session['email'] = email
            session['role'] = role
            return jsonify({
                'success': True,
                'user_id': f"{email}_{role}",
                'user': {
                    'email': email,
                    'role': role,
                    'exnova_connected': True
                }
            })
        else:
            return jsonify({'error': 'Error conectando con ExNova'}), 400
            
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/follower/start-bot', methods=['POST'])
def start_follower_bot_api():
    """Encender bot del seguidor"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        success = start_follower_bot(email)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Bot del seguidor encendido exitosamente'
            })
        else:
            return jsonify({'error': 'Error encendiendo bot del seguidor'}), 500
            
    except Exception as e:
        logger.error(f"Error encendiendo bot: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/follower/stop-bot', methods=['POST'])
def stop_follower_bot_api():
    """Apagar bot del seguidor"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email requerido'}), 400
        
        success = stop_follower_bot(email)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Bot del seguidor apagado exitosamente'
            })
        else:
            return jsonify({'error': 'Error apagando bot del seguidor'}), 500
            
    except Exception as e:
        logger.error(f"Error apagando bot: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/follower/bot-status', methods=['GET'])
def get_follower_bot_status_api():
    """Obtener estado del bot del seguidor"""
    try:
        email = session.get('email')
        if not email:
            return jsonify({'error': 'No autorizado'}), 401
        
        bot_status = get_follower_bot_status(email)
        
        return jsonify({
            'success': True,
            'bot_status': bot_status
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/trader/start-auto-copy', methods=['POST'])
def start_auto_copy():
    """Activar copytrading automático"""
    try:
        if not trader_connection:
            return jsonify({'error': 'No hay trader conectado'}), 400
        
        success = start_auto_copy_monitoring()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'COPYTRADING AUTOMÁTICO ACTIVADO'
            })
        else:
            return jsonify({'error': 'Error iniciando auto-copy'}), 500
            
    except Exception as e:
        logger.error(f"Error iniciando auto-copy: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/trader/stop-auto-copy', methods=['POST'])
def stop_auto_copy():
    """Detener copytrading automático"""
    try:
        stop_auto_copy_monitoring()
        return jsonify({
            'success': True,
            'message': 'COPYTRADING AUTOMÁTICO DETENIDO'
        })
        
    except Exception as e:
        logger.error(f"Error deteniendo auto-copy: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Obtener estado del sistema"""
    try:
        return jsonify({
            'success': True,
            'trader_connected': trader_connection is not None,
            'followers_count': len(follower_connections),
            'auto_copy_active': auto_copy_active
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo estado: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

# WebSocket events
@socketio.on('connect')
def handle_connect():
    logger.info(f"🔌 Cliente conectado: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"🔌 Cliente desconectado: {request.sid}")

if __name__ == '__main__':
    logger.info("🚀 Iniciando Simple Web Bot...")
    logger.info("📊 Sistema de Copytrading Web Simplificado")
    logger.info("🌐 Sin procesos independientes")
    logger.info("🔗 API REST + WebSocket")
    
    socketio.run(app, host='0.0.0.0', port=5005, debug=False, allow_unsafe_werkzeug=True)
