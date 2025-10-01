"""
Configuración para Metabinario Web Backend
"""

import os

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'metabinario_web_secret_key_2025'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'metabinario_jwt_secret_2025'
    
    # Configuración de ExNova API
    EXNOVA_API_PATH = '/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado'
    
    # Configuración de base de datos
    DATABASE_PATH = 'database/'
    FOLLOWERS_DB_FILE = 'followers.json'
    USERS_DB_FILE = 'users.json'
    
    # Configuración de WebSocket
    SOCKETIO_CORS_ALLOWED_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Configuración de logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuración de copytrading
    DEFAULT_BALANCE_MODE = 'PRACTICE'
    DEFAULT_AMOUNT = 10.0
    DEFAULT_DURATION = 2
    DEFAULT_ACTIVE = 'EURUSD-OTC'

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
