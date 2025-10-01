#!/usr/bin/env python3
"""
Monitor de logs en tiempo real para el sistema de copytrading
"""

import subprocess
import time
import signal
import sys
from datetime import datetime

class LogMonitor:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        print("\n🛑 Deteniendo monitor de logs...")
        self.running = False
        sys.exit(0)
    
    def monitor_backend_logs(self):
        """Monitorear logs del backend en tiempo real"""
        print("🔍 INICIANDO MONITOR DE LOGS")
        print("=" * 60)
        print(f"⏰ Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("📋 Monitoreando logs del backend...")
        print("🎯 Ejecuta una entrada en ExNova para ver la replicación")
        print("🛑 Presiona Ctrl+C para detener")
        print("=" * 60)
        print()
        
        try:
            # Monitorear el proceso del backend
            process = subprocess.Popen(
                ['ps', 'aux'], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            stdout, stderr = process.communicate()
            
            # Buscar el proceso del backend
            backend_processes = []
            for line in stdout.split('\n'):
                if 'python' in line and 'app' in line and '5003' in line:
                    backend_processes.append(line.strip())
            
            if backend_processes:
                print("✅ Backend detectado y funcionando")
                print(f"📊 Procesos activos: {len(backend_processes)}")
                print()
                
                # Monitorear conexiones
                self.monitor_connections()
                
            else:
                print("❌ No se detectó el proceso del backend")
                print("💡 Asegúrate de que el bot esté ejecutándose")
                
        except Exception as e:
            print(f"❌ Error monitoreando: {e}")
    
    def monitor_connections(self):
        """Monitorear conexiones de red"""
        print("🌐 MONITOREANDO CONEXIONES:")
        print("-" * 40)
        
        try:
            # Verificar puerto 5003
            result = subprocess.run(
                ['lsof', '-i', ':5003'], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Puerto 5003: ACTIVO")
                for line in result.stdout.split('\n')[1:]:  # Saltar header
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            print(f"   📡 {parts[0]} - {parts[1]}")
            else:
                print("❌ Puerto 5003: NO ACTIVO")
            
            # Verificar puerto 8000
            result = subprocess.run(
                ['lsof', '-i', ':8000'], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Puerto 8000: ACTIVO")
            else:
                print("❌ Puerto 8000: NO ACTIVO")
                
        except Exception as e:
            print(f"❌ Error verificando conexiones: {e}")
        
        print()
        print("🎯 INSTRUCCIONES:")
        print("1. Abre http://localhost:8000 en tu navegador")
        print("2. Configura tu cuenta de trader")
        print("3. Agrega cuentas de seguidores")
        print("4. Activa el monitoreo automático")
        print("5. Ejecuta una entrada en ExNova")
        print("6. Observa los logs aquí en tiempo real")
        print()
        print("⏳ Esperando actividad... (Presiona Ctrl+C para salir)")
        
        # Monitoreo continuo
        while self.running:
            time.sleep(1)
            
            # Verificar estado de la API
            try:
                import requests
                response = requests.get("http://localhost:5003/api/status", timeout=2)
                if response.status_code == 200:
                    # API funcionando, continuar monitoreo
                    pass
                else:
                    print(f"⚠️  API respondió con código: {response.status_code}")
            except:
                print("⚠️  No se puede conectar a la API")
                break

if __name__ == "__main__":
    monitor = LogMonitor()
    monitor.monitor_backend_logs()

