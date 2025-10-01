# Metabinario Web Backend

Sistema de Copytrading Web sin dependencias de Telegram.

## 🚀 Características

- **API REST** completa para gestión de copytrading
- **WebSocket** para notificaciones en tiempo real
- **Autenticación JWT** segura
- **Integración completa** con ExNova API
- **Base de datos JSON** para persistencia
- **Sin dependencias de Telegram**

## 📋 Requisitos

- Python 3.8+
- ExNova API (ubicada en `/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado`)

## 🛠️ Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Ejecutar el servidor:**
```bash
python run.py
```

3. **Acceder a la API:**
- API REST: http://localhost:5000
- WebSocket: ws://localhost:5000

## 📚 Endpoints de la API

### Autenticación
- `POST /api/login` - Iniciar sesión
- `POST /api/register` - Registrar usuario
- `POST /api/logout` - Cerrar sesión

### Gestión de Traders
- `POST /api/trader/add` - Agregar cuenta trader
- `GET /api/trader/status` - Estado del trader
- `POST /api/trader/start-monitoring` - Iniciar monitoreo
- `POST /api/trader/stop-monitoring` - Detener monitoreo

### Gestión de Seguidores
- `POST /api/follower/add` - Agregar seguidor
- `GET /api/followers` - Lista de seguidores
- `POST /api/follower/remove` - Remover seguidor

### Copytrading
- `POST /api/copytrading/manual` - Copytrading manual
- `POST /api/copytrading/auto/start` - Iniciar automático
- `POST /api/copytrading/auto/stop` - Detener automático
- `GET /api/copytrading/status` - Estado del copytrading

## 🔌 WebSocket Events

### Cliente → Servidor
- `join_room` - Unirse a una sala
- `leave_room` - Salir de una sala

### Servidor → Cliente
- `notification` - Notificación general
- `copytrading_result` - Resultado de copytrading
- `new_operation` - Nueva operación detectada
- `follower_status` - Estado de seguidor
- `system_alert` - Alerta del sistema
- `balance_update` - Actualización de balance
- `trading_stats` - Estadísticas de trading

## 📁 Estructura de Archivos

```
backend/
├── app.py              # Aplicación Flask principal
├── config.py           # Configuraciones
├── database.py         # Gestión de base de datos
├── notifications.py    # Sistema de notificaciones web
├── run.py             # Script de inicio
├── requirements.txt   # Dependencias
└── README.md         # Documentación
```

## 🔧 Configuración

### Variables de Entorno
- `SECRET_KEY` - Clave secreta de Flask
- `JWT_SECRET_KEY` - Clave secreta para JWT
- `EXNOVA_API_PATH` - Ruta a la API de ExNova

### Base de Datos
Los datos se almacenan en archivos JSON en el directorio `database/`:
- `followers.json` - Base de datos de seguidores
- `users.json` - Base de datos de usuarios
- `operations.json` - Historial de operaciones

## 🚨 Notas Importantes

1. **Sin Telegram**: Este backend NO tiene dependencias de Telegram
2. **ExNova API**: Requiere que la API de ExNova esté disponible
3. **WebSocket**: Usa Flask-SocketIO para notificaciones en tiempo real
4. **Seguridad**: Usa JWT para autenticación
5. **Persistencia**: Base de datos JSON para simplicidad

## 🐛 Solución de Problemas

### Error de conexión a ExNova
Verificar que la ruta `/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado` existe y contiene la API de ExNova.

### Error de WebSocket
Verificar que el puerto 5000 esté disponible y que CORS esté configurado correctamente.

### Error de base de datos
Verificar permisos de escritura en el directorio `database/`.

## 📞 Soporte

Para soporte técnico, revisar los logs del servidor o contactar al desarrollador.
