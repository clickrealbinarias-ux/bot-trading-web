#!/bin/bash

echo "🔧 INSTALANDO TODAS LAS DEPENDENCIAS NECESARIAS"
echo "=============================================="

# Activar entorno virtual
echo "📦 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias del backend
echo "📦 Instalando dependencias del backend..."
pip install --upgrade pip
pip install Flask==2.3.3
pip install Flask-SocketIO==5.3.6
pip install Flask-CORS==4.0.0
pip install PyJWT==2.8.0
pip install python-socketio==5.9.0
pip install eventlet==0.33.3
pip install requests==2.32.5
pip install websockets==15.0.1

# Instalar dependencias adicionales necesarias
echo "📦 Instalando dependencias adicionales..."
pip install websocket-client==1.6.4
pip install numpy
pip install pandas
pip install python-dotenv

# Verificar instalación
echo "✅ Verificando instalación..."
python3 -c "
import sys
print('Python:', sys.version)

deps = ['Flask', 'Flask_SocketIO', 'Flask_CORS', 'jwt', 'socketio', 'eventlet', 'requests', 'websockets', 'websocket']
for dep in deps:
    try:
        __import__(dep)
        print(f'✅ {dep}')
    except ImportError as e:
        print(f'❌ {dep}: {e}')

# Probar websocket específicamente
try:
    import websocket
    print(f'✅ websocket desde: {websocket.__file__}')
    ws = websocket.WebSocketApp('ws://test')
    print(f'✅ WebSocketApp creado')
    print(f'✅ run_forever disponible: {hasattr(ws, \"run_forever\")}')
except Exception as e:
    print(f'❌ Error con websocket: {e}')
"

echo "🎉 Instalación completada!"

