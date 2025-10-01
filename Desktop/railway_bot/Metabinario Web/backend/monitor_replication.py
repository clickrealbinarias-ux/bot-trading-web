#!/usr/bin/env python3
"""
MONITOR DE REPLICACIÓN EN TIEMPO REAL
"""

import subprocess
import time
import re

def monitor_replication():
    """Monitorear replicación en tiempo real"""
    print("🔍 MONITOR DE REPLICACIÓN EN TIEMPO REAL")
    print("=" * 60)
    print("📡 Monitoreando logs para detectar operaciones y replicación...")
    print("💡 Presiona Ctrl+C para detener")
    print("-" * 60)
    
    try:
        # Ejecutar tail -f en el archivo de logs
        process = subprocess.Popen(
            ['tail', '-f', '/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend/copytrading_web.log'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        operation_count = 0
        replication_count = 0
        
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            
            # Detectar operaciones nuevas
            if 'NUEVA OPERACIÓN DETECTADA' in line:
                operation_count += 1
                print(f"\n🎯 OPERACIÓN #{operation_count} DETECTADA:")
                print(f"   {line}")
            
            # Detectar replicación
            elif 'Replicando operación' in line:
                print(f"🔄 REPLICACIÓN:")
                print(f"   {line}")
                
                # Extraer número de seguidores
                match = re.search(r'a (\d+) seguidores', line)
                if match:
                    followers_count = int(match.group(1))
                    if followers_count > 0:
                        replication_count += 1
                        print(f"   ✅ REPLICANDO A {followers_count} SEGUIDORES")
                    else:
                        print(f"   ⚠️ NO HAY SEGUIDORES ACTIVOS")
            
            # Detectar estado de seguidores
            elif 'Seguidor con bot' in line:
                print(f"🤖 ESTADO SEGUIDOR:")
                print(f"   {line}")
            
            # Detectar resultados
            elif 'Resultados seguidores' in line:
                print(f"📊 RESULTADOS:")
                print(f"   {line}")
                
                # Mostrar resumen
                print(f"\n📈 RESUMEN:")
                print(f"   Operaciones detectadas: {operation_count}")
                print(f"   Replicaciones exitosas: {replication_count}")
                print("-" * 60)
    
    except KeyboardInterrupt:
        print(f"\n🛑 Monitor detenido")
        print(f"📈 RESUMEN FINAL:")
        print(f"   Operaciones detectadas: {operation_count}")
        print(f"   Replicaciones exitosas: {replication_count}")
        process.terminate()
    except Exception as e:
        print(f"❌ Error en monitor: {e}")
        process.terminate()

if __name__ == "__main__":
    monitor_replication()





