#!/usr/bin/env python3
"""
INICIADOR DEL BOT WEB CON MONITOR DE COMPARACIÓN
Ejecuta el bot web y el monitor de comparación en paralelo
"""

import subprocess
import sys
import os
import time
import signal
import threading
from datetime import datetime

def start_bot_web():
    """Iniciar el bot web"""
    print("🚀 Iniciando Bot Web...")
    try:
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Leer salida en tiempo real
        def read_output():
            for line in iter(process.stdout.readline, ''):
                print(f"[BOT WEB] {line.strip()}")
        
        def read_error():
            for line in iter(process.stderr.readline, ''):
                print(f"[BOT WEB ERROR] {line.strip()}")
        
        # Crear threads para leer salida
        output_thread = threading.Thread(target=read_output, daemon=True)
        error_thread = threading.Thread(target=read_error, daemon=True)
        
        output_thread.start()
        error_thread.start()
        
        return process
    except Exception as e:
        print(f"❌ Error iniciando bot web: {e}")
        return None

def start_monitor():
    """Iniciar el monitor de comparación"""
    print("🔍 Iniciando Monitor de Comparación...")
    try:
        process = subprocess.Popen([
            sys.executable, "monitor_comparison.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Leer salida en tiempo real
        def read_output():
            for line in iter(process.stdout.readline, ''):
                print(f"[MONITOR] {line.strip()}")
        
        def read_error():
            for line in iter(process.stderr.readline, ''):
                print(f"[MONITOR ERROR] {line.strip()}")
        
        # Crear threads para leer salida
        output_thread = threading.Thread(target=read_output, daemon=True)
        error_thread = threading.Thread(target=read_error, daemon=True)
        
        output_thread.start()
        error_thread.start()
        
        return process
    except Exception as e:
        print(f"❌ Error iniciando monitor: {e}")
        return None

def signal_handler(sig, frame):
    """Manejar señales de interrupción"""
    print("\n🛑 Deteniendo procesos...")
    if 'bot_process' in globals() and bot_process:
        bot_process.terminate()
    if 'monitor_process' in globals() and monitor_process:
        monitor_process.terminate()
    sys.exit(0)

def main():
    """Función principal"""
    print("=" * 70)
    print("🚀 INICIADOR DEL BOT WEB CON MONITOR DE COMPARACIÓN")
    print("=" * 70)
    print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Cambiar al directorio del backend
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Activar entorno virtual
    venv_python = os.path.join(os.getcwd(), "venv", "bin", "python3")
    if not os.path.exists(venv_python):
        print(f"❌ Error: No se encontró el entorno virtual en {venv_python}")
        print("Por favor, asegúrate de haber creado y activado el entorno virtual.")
        sys.exit(1)
    
    # Iniciar bot web
    global bot_process
    bot_process = start_bot_web()
    if not bot_process:
        print("❌ No se pudo iniciar el bot web")
        sys.exit(1)
    
    # Esperar un poco para que el bot web se inicie
    print("⏳ Esperando que el bot web se inicie...")
    time.sleep(5)
    
    # Iniciar monitor
    global monitor_process
    monitor_process = start_monitor()
    if not monitor_process:
        print("❌ No se pudo iniciar el monitor")
        bot_process.terminate()
        sys.exit(1)
    
    print("✅ Ambos procesos iniciados correctamente")
    print("🌐 Bot Web: http://localhost:5003")
    print("📊 Monitor: Verificando comparación en tiempo real")
    print("=" * 70)
    print("Presiona Ctrl+C para detener ambos procesos")
    print("=" * 70)
    
    try:
        # Mantener ambos procesos activos
        while True:
            # Verificar si el bot web sigue activo
            if bot_process.poll() is not None:
                print("❌ El bot web se detuvo inesperadamente")
                break
            
            # Verificar si el monitor sigue activo
            if monitor_process.poll() is not None:
                print("❌ El monitor se detuvo inesperadamente")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo procesos...")
    finally:
        # Terminar procesos
        if bot_process:
            bot_process.terminate()
            bot_process.wait()
        if monitor_process:
            monitor_process.terminate()
            monitor_process.wait()
        print("✅ Procesos detenidos correctamente")

if __name__ == "__main__":
    main()

