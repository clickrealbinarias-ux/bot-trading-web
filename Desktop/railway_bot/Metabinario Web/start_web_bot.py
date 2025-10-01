#!/usr/bin/env python3
"""
Script de inicio para Metabinario Web Bot
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    try:
        import flask
        import flask_socketio
        print("✅ Dependencias de Flask encontradas")
        return True
    except ImportError as e:
        print(f"❌ Dependencias faltantes: {e}")
        print("Instalando dependencias...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
            print("✅ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando dependencias")
            return False

def start_backend():
    """Iniciar el backend"""
    print("🚀 Iniciando backend...")
    os.chdir("backend")
    
    try:
        # Ejecutar el backend
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n⏹️ Backend detenido")
    except Exception as e:
        print(f"❌ Error iniciando backend: {e}")

def main():
    """Función principal"""
    print("🤖 Metabinario Web Bot - Iniciando...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ No se pudieron instalar las dependencias")
        return
    
    # Crear directorio de base de datos si no existe
    os.makedirs("backend/database", exist_ok=True)
    
    print("📁 Directorio de base de datos creado")
    print("🌐 El bot estará disponible en: http://localhost:5003")
    print("📱 Frontend disponible en: http://localhost:5003 (servido por Flask)")
    print("=" * 50)
    
    # Iniciar backend
    start_backend()

if __name__ == "__main__":
    main()

