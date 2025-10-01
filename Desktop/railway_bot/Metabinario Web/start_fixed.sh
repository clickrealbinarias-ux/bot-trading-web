#!/bin/bash

# Metabinario Web - Script de Inicio CORREGIDO
# Sin conflictos de puertos, sin modo debug

echo "🚀 Iniciando Metabinario Web (VERSIÓN CORREGIDA)..."
echo "📊 Sistema de Copytrading Web"
echo "🌐 Sin dependencias de Telegram"
echo "🔧 Puerto 5001 (sin conflicto AirPlay)"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_message() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Detener procesos existentes
echo "🧹 Limpiando procesos existentes..."
pkill -f "python.*run.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null
sleep 2

# Verificar Python
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 no está instalado"
    exit 1
fi
show_message "Python 3 encontrado"

# Verificar API de ExNova
EXNOVA_PATH="/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado"
if [ ! -d "$EXNOVA_PATH" ]; then
    show_error "No se encontró la API de ExNova en: $EXNOVA_PATH"
    exit 1
fi
show_message "API de ExNova encontrada"

# Activar entorno virtual
show_message "Activando entorno virtual..."
source venv/bin/activate

# Iniciar backend
show_message "Iniciando backend en puerto 5001..."
cd backend
python3 run.py &
BACKEND_PID=$!
cd ..

# Esperar que el backend se inicie
sleep 5

# Verificar backend
if curl -s http://localhost:5001/api/status > /dev/null; then
    show_message "Backend iniciado correctamente en http://localhost:5001"
else
    show_error "Error iniciando el backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Iniciar frontend
show_message "Iniciando frontend en puerto 8000..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

# Esperar que el frontend se inicie
sleep 3

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
echo "🔧 Backend API: http://localhost:5001"
echo "📡 WebSocket: ws://localhost:5001"
echo ""
echo "👤 Usuario demo: demo_user / demo123"
echo ""
echo "🛑 Para detener: pkill -f 'python.*run.py' && pkill -f 'http.server'"
echo ""

# Función de limpieza
cleanup() {
    echo ""
    show_warning "Deteniendo servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    show_message "Servidores detenidos"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Mantener el script ejecutándose
wait

