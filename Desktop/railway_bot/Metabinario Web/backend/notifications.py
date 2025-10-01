"""
Sistema de notificaciones web para Metabinario
Reemplaza las notificaciones de Telegram
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from flask_socketio import emit

logger = logging.getLogger(__name__)

class WebNotificationManager:
    """Gestor de notificaciones web"""
    
    def __init__(self, socketio_instance):
        self.socketio = socketio_instance
    
    def send_notification(self, user_id: str, notification_type: str, data: Dict[str, Any]):
        """Enviar notificación a un usuario específico"""
        try:
            notification = {
                'type': notification_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'id': f"{notification_type}_{int(datetime.now().timestamp())}"
            }
            
            self.socketio.emit('notification', notification, room=user_id)
            logger.info(f"Notificación enviada a {user_id}: {notification_type}")
            
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
    
    def send_broadcast(self, notification_type: str, data: Dict[str, Any]):
        """Enviar notificación a todos los usuarios conectados"""
        try:
            notification = {
                'type': notification_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'id': f"{notification_type}_{int(datetime.now().timestamp())}"
            }
            
            self.socketio.emit('broadcast', notification)
            logger.info(f"Broadcast enviado: {notification_type}")
            
        except Exception as e:
            logger.error(f"Error enviando broadcast: {e}")
    
    def send_copytrading_result(self, user_id: str, results: Dict[str, Any]):
        """Enviar resultado de copytrading"""
        self.send_notification(user_id, 'copytrading_result', {
            'success': results.get('success', False),
            'total_operations': results.get('total_operations', 0),
            'successful_operations': results.get('successful_operations', 0),
            'trader_result': results.get('trader_result'),
            'follower_results': results.get('follower_results', [])
        })
    
    def send_new_operation_detected(self, user_id: str, operation_data: Dict[str, Any]):
        """Enviar notificación de nueva operación detectada"""
        self.send_notification(user_id, 'new_operation', {
            'operation_id': operation_data.get('operation_id'),
            'active': operation_data.get('active'),
            'direction': operation_data.get('direction'),
            'amount': operation_data.get('amount'),
            'duration': operation_data.get('duration')
        })
    
    def send_follower_status_update(self, user_id: str, follower_email: str, status: str):
        """Enviar actualización de estado de seguidor"""
        self.send_notification(user_id, 'follower_status', {
            'email': follower_email,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    
    def send_system_alert(self, user_id: str, message: str, alert_type: str = 'info'):
        """Enviar alerta del sistema"""
        self.send_notification(user_id, 'system_alert', {
            'message': message,
            'alert_type': alert_type,  # info, warning, error, success
            'timestamp': datetime.now().isoformat()
        })
    
    def send_balance_update(self, user_id: str, balance_data: Dict[str, Any]):
        """Enviar actualización de balance"""
        self.send_notification(user_id, 'balance_update', {
            'balance': balance_data.get('balance'),
            'currency': balance_data.get('currency'),
            'change': balance_data.get('change', 0),
            'timestamp': datetime.now().isoformat()
        })
    
    def send_trading_stats(self, user_id: str, stats: Dict[str, Any]):
        """Enviar estadísticas de trading"""
        self.send_notification(user_id, 'trading_stats', {
            'total_trades': stats.get('total_trades', 0),
            'successful_trades': stats.get('successful_trades', 0),
            'win_rate': stats.get('win_rate', 0),
            'total_profit': stats.get('total_profit', 0),
            'timestamp': datetime.now().isoformat()
        })

# Funciones de conveniencia para reemplazar las notificaciones de Telegram
def send_telegram_replacement_notification(user_id: str, message: str, notification_type: str = 'info'):
    """Función de conveniencia para reemplazar notificaciones de Telegram"""
    # Esta función se puede usar como reemplazo directo de bot.send_message
    pass  # Se implementará cuando se instancie el WebNotificationManager

def format_copytrading_message(operation_data: Dict[str, Any]) -> str:
    """Formatear mensaje de copytrading (reemplaza formato de Telegram)"""
    active = operation_data.get('active', 'N/A')
    direction = operation_data.get('direction', 'N/A')
    amount = operation_data.get('amount', 0)
    result = operation_data.get('result', 'N/A')
    
    direction_text = "COMPRA" if direction == "CALL" else "VENTA"
    
    return f"""
🤖 **COPYTRADING AUTOMÁTICO**

- **Divisa:** {active}
- **Dirección:** {direction_text}
- **Importe:** ${amount}
- **Resultado:** {result}
- **Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

def format_trader_operation_message(active: str, direction: str, duration: int, follower_results: Dict[str, str]) -> str:
    """Formatear mensaje de operación del trader"""
    emoji = "🟢" if direction == "CALL" else "🔴"
    arrow = "⬆️" if direction == "CALL" else "⬇️"
    
    follower_status = " | ".join([f"👤 {name} {status}" for name, status in follower_results.items()])
    
    return f"""
{emoji} {active} {arrow} {direction} {duration}m
{follower_status}
"""
