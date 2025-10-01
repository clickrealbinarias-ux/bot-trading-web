#!/usr/bin/env python3
"""
Servidor web simple para el frontend
"""

import http.server
import socketserver
import os
import sys

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Agregar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

def start_server():
    """Iniciar servidor web simple"""
    PORT = 8000
    
    # Cambiar al directorio frontend
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    os.chdir(frontend_dir)
    
    print(f"🌐 Iniciando servidor web en puerto {PORT}")
    print(f"📁 Directorio: {frontend_dir}")
    print(f"🔗 URL: http://localhost:{PORT}")
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"✅ Servidor iniciado en http://localhost:{PORT}")
            print("🛑 Presiona Ctrl+C para detener")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    start_server()

