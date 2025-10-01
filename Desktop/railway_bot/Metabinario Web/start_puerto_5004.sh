#!/bin/bash

echo "🚀 Iniciando Metabinario Web en Puerto 5004..."
echo "📊 Sistema de Copytrading Web"
echo "🌐 Sin dependencias de Telegram"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado"
    exit 1
fi
echo "✅ Python 3 encontrado"

# Verificar API de ExNova
if [ ! -d "/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/exnovaapi" ]; then
    echo "❌ API de ExNova no encontrada"
    exit 1
fi
echo "✅ API de ExNova encontrada"

# Activar entorno virtual
echo "ℹ️  Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias del backend
echo "ℹ️  Instalando dependencias del backend..."
pip install -r backend/requirements.txt

# Instalar websocket-client si no está instalado
echo "ℹ️  Verificando websocket-client..."
pip install websocket-client==1.6.4

# Iniciar backend en puerto 5004
echo "ℹ️  Iniciando backend en puerto 5004..."
cd backend
python3 run.py &
BACKEND_PID=$!

# Esperar un momento para que el backend se inicie
sleep 3

# Verificar que el backend esté funcionando
if curl -s http://localhost:5004/api/status > /dev/null; then
    echo "✅ Backend iniciado correctamente en http://localhost:5004"
else
    echo "❌ Error iniciando backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Iniciar frontend
echo "ℹ️  Iniciando frontend en puerto 8000..."
cd ../frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!

# Esperar un momento para que el frontend se inicie
sleep 2

# Verificar que el frontend esté funcionando
if curl -s http://localhost:8000 > /dev/null; then
    echo "✅ Frontend iniciado correctamente en http://localhost:8000"
else
    echo "❌ Error iniciando frontend"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Metabinario Web está funcionando!"
echo "📱 Frontend: http://localhost:8000"
echo "🔧 Backend API: http://localhost:5004"
echo "📡 WebSocket: ws://localhost:5004"
echo "👤 Usuario demo: demo_user / demo123"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ Servidores detenidos"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Mantener el script corriendo
wait

