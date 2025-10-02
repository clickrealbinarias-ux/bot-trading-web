#!/usr/bin/env python3
"""
ARCHIVO PRINCIPAL PARA RENDER - SOLUCIÓN ROBUSTA
Render busca automáticamente main.py como punto de entrada
"""

import os
import sys
import logging
from web_app import app, copy_manager, logger

# Configuración específica para Render
def configure_for_render():
    """Configurar la aplicación para funcionar en Render"""
    
    # Configurar logging para producción
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configurar Flask para producción
    app.config['DEBUG'] = False
    app.config['ENV'] = 'production'
    
    # Configurar host y puerto para Render
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'
    
    return host, port

def start_render_server():
    """Iniciar el servidor optimizado para Render"""
    try:
        host, port = configure_for_render()
        
        logger.info("🚀 Iniciando Meta Binario Copy Trading en Render")
        logger.info(f"🌐 Servidor configurado para: {host}:{port}")
        logger.info("📊 Sistema de copy trading listo para producción")
        
        # Iniciar servidor Flask
        app.run(
            debug=False,
            host=host,
            port=port,
            threaded=True,
            use_reloader=False
        )
        
    except Exception as e:
        logger.error(f"❌ Error iniciando servidor en Render: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_render_server()
