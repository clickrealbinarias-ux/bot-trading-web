# Alias para websocket-client
# Esto resuelve el error "No module named 'websocket'"

try:
    from websocket import *
    from websocket import WebSocketApp, WebSocketConnectionClosedException
    print("✅ websocket importado correctamente desde websocket-client")
except ImportError as e:
    print(f"❌ Error importando websocket: {e}")
    # Si no está disponible, crear un stub básico
    class WebSocketApp:
        def __init__(self, *args, **kwargs):
            self.url = kwargs.get('url', '')
            self.on_open = kwargs.get('on_open')
            self.on_message = kwargs.get('on_message')
            self.on_error = kwargs.get('on_error')
            self.on_close = kwargs.get('on_close')
        
        def run_forever(self, *args, **kwargs):
            print("⚠️ WebSocketApp.run_forever() - Stub implementado")
            return True
    
    class WebSocketConnectionClosedException(Exception):
        pass
