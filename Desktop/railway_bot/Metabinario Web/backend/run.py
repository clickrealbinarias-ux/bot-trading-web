#!/usr/bin/env python3
"""
Script para ejecutar el Metabinario Web Bot
"""

import sys
import os

# Agregar el directorio raíz al path para importar our_copytrading_api
sys.path.append('/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado')

if __name__ == '__main__':
    from metabinario_web import app, socketio
    
    print("🚀 Iniciando Metabinario Web Backend...")
    print("📊 Sistema de Copytrading Web")
    print("🌐 Sin dependencias de Telegram")
    print("🔗 API REST + WebSocket")
    print("✅ API de ExNova encontrada en: /Users/rick/Desktop/BOTTELEGRAM/metabot_modificado")
    print("🌐 Iniciando servidor en http://localhost:5004")
    print("📡 WebSocket disponible en ws://localhost:5004")
    print("📚 Documentación API en http://localhost:5004")
    
    socketio.run(app, host='0.0.0.0', port=5004, debug=False, allow_unsafe_werkzeug=True)