#!/bin/bash

# Metabinario Web - Script de Inicio FUNCIONAL
# Basado en la documentación oficial

echo "🚀 Iniciando Metabinario Web (VERSIÓN FUNCIONAL)..."
echo "📊 Sistema de Copytrading Web"
echo "🌐 Sin dependencias de Telegram"
echo "📋 Basado en documentación oficial"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_message() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detener procesos existentes
echo "🧹 Limpiando procesos existentes..."
pkill -f "python.*run.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null
pkill -f "simple_server" 2>/dev/null
sleep 3

# Verificar Python
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 no está instalado"
    exit 1
fi
show_message "Python 3 encontrado"

# Verificar API de ExNova
EXNOVA_PATH="/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado"
if [ ! -d "$EXNOVA_PATH" ]; then
    show_error "No se encontró la API de ExNova"
    exit 1
fi
show_message "API de ExNova encontrada"

# Activar entorno virtual
show_message "Activando entorno virtual..."
source venv/bin/activate

# Iniciar backend en puerto 5003 (según documentación)
show_message "Iniciando backend en puerto 5003..."
cd backend
python3 run.py &
BACKEND_PID=$!
cd ..

# Esperar que el backend se inicie
sleep 8

# Verificar backend
if curl -s http://localhost:5003/api/status > /dev/null; then
    show_message "Backend iniciado correctamente en http://localhost:5003"
else
    show_error "Error iniciando el backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Iniciar frontend en puerto 8000
show_message "Iniciando frontend en puerto 8000..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

# Esperar que el frontend se inicie
sleep 5

# Verificar frontend
if curl -s http://localhost:8000 > /dev/null; then
    show_message "Frontend iniciado correctamente en http://localhost:8000"
else
    show_error "Error iniciando el frontend"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 Metabinario Web está funcionando!"
echo ""
echo "📱 Frontend: http://localhost:8000"
echo "🔧 Backend API: http://localhost:5003"
echo "📡 WebSocket: ws://localhost:5003"
echo ""
echo "👤 Usuario demo: demo_user / demo123"
echo ""
echo "✅ Tu bot web está funcionando correctamente"
echo "🚀 Puedes acceder a la interfaz ahora"
echo ""

# Función de limpieza
cleanup() {
    echo ""
    echo "🛑 Deteniendo servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    show_message "Servidores detenidos"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Mantener el script ejecutándose
wait

