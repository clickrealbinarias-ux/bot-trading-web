#!/bin/bash

# Metabinario Web - Script de Inicio
# Sistema de Copytrading Web sin dependencias de Telegram

echo "🚀 Iniciando Metabinario Web..."
echo "📊 Sistema de Copytrading Web"
echo "🌐 Sin dependencias de Telegram"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
show_message() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    show_error "Python 3 no está instalado"
    exit 1
fi

show_message "Python 3 encontrado"

# Verificar que la API de ExNova esté disponible
EXNOVA_PATH="/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado"
if [ ! -d "$EXNOVA_PATH" ]; then
    show_error "No se encontró la API de ExNova en: $EXNOVA_PATH"
    exit 1
fi

show_message "API de ExNova encontrada"

# Navegar al directorio del backend
cd backend

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    show_info "Creando entorno virtual..."
    python3 -m venv venv
fi

# Activar entorno virtual
show_info "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
show_info "Instalando dependencias del backend..."
pip install -r requirements.txt

# Crear directorio de base de datos
mkdir -p database

# Iniciar backend en segundo plano
show_info "Iniciando backend en puerto 5000..."
python run.py &
BACKEND_PID=$!

# Esperar un momento para que el backend se inicie
sleep 3

# Verificar que el backend esté funcionando
if curl -s http://localhost:5000 > /dev/null; then
    show_message "Backend iniciado correctamente en http://localhost:5000"
else
    show_error "Error iniciando el backend"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Navegar al directorio del frontend
cd ../frontend

# Iniciar servidor del frontend
show_info "Iniciando frontend en puerto 8000..."
python3 -m http.server 8000 &
FRONTEND_PID=$!

# Esperar un momento para que el frontend se inicie
sleep 2

# Verificar que el frontend esté funcionando
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
echo "🔧 Backend API: http://localhost:5000"
echo "📡 WebSocket: ws://localhost:5000"
echo ""
echo "👤 Usuario demo: demo_user / demo123"
echo ""
echo "Para detener el servidor, presiona Ctrl+C"

# Función para limpiar procesos al salir
cleanup() {
    echo ""
    show_info "Deteniendo servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    show_message "Servidores detenidos"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

# Mantener el script ejecutándose
wait
