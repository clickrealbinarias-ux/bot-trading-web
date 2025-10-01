# 🤖 Metabinario Web Bot - Sistema de Copytrading Automático

## 📋 Descripción

Metabinario Web Bot es una plataforma web completa para copytrading automático que permite a los traders ejecutar operaciones y a los seguidores copiar automáticamente esas operaciones en tiempo real.

## ✨ Características Principales

### 🔐 Sistema de Autenticación
- **Login dual**: Traders y Seguidores
- **Conexión directa con ExNova**: Sin dependencias de Telegram
- **Gestión de sesiones**: Control individual por usuario

### 📈 Para Traders
- **Dashboard completo**: Monitoreo en tiempo real
- **Copytrading automático**: Activar/desactivar con un clic
- **Gestión de seguidores**: Ver todos los seguidores conectados
- **Notificaciones en tiempo real**: WebSocket para actualizaciones instantáneas

### 👥 Para Seguidores
- **Control individual del bot**: Encender/apagar independientemente
- **Configuración de importe**: Personalizar cantidad por operación
- **Modo Demo/Real**: Elegir entre práctica o dinero real
- **Notificaciones de operaciones**: Recibir alertas de nuevas operaciones

### 🔧 Características Técnicas
- **API REST completa**: Endpoints para todas las funcionalidades
- **WebSocket en tiempo real**: Notificaciones instantáneas
- **Base de datos JSON**: Almacenamiento simple y eficiente
- **Arquitectura modular**: Fácil mantenimiento y expansión
- **Interfaz moderna**: UI/UX profesional y responsive

## 🚀 Instalación y Uso

### Requisitos Previos
- Python 3.8+
- Cuentas de ExNova (Demo o Real)

### Instalación Rápida
```bash
# 1. Navegar al directorio del bot
cd "Metabinario Web"

# 2. Ejecutar script de inicio
python start_web_bot.py
```

### Instalación Manual
```bash
# 1. Instalar dependencias
pip install -r backend/requirements.txt

# 2. Iniciar backend
cd backend
python app.py
```

### Acceso
- **URL**: http://localhost:5003
- **Puerto**: 5003 (configurable)

## 📁 Estructura del Proyecto

```
Metabinario Web/
├── backend/
│   ├── app.py                 # Aplicación Flask principal
│   ├── our_copytrading_api.py # API de copytrading
│   ├── database.py           # Gestor de base de datos
│   ├── requirements.txt      # Dependencias Python
│   └── database/             # Archivos JSON de datos
├── frontend/
│   ├── index.html           # Interfaz principal
│   ├── script.js           # JavaScript del frontend
│   └── styles.css          # Estilos CSS
├── start_web_bot.py        # Script de inicio
└── README.md              # Este archivo
```

## 🔌 API Endpoints

### Autenticación
- `POST /api/login` - Login de usuario
- `POST /api/follower/register` - Registro de seguidor

### Trader
- `GET /api/trader/status` - Estado del trader
- `POST /api/trader/start-auto-copy` - Iniciar copytrading automático
- `POST /api/trader/stop-auto-copy` - Detener copytrading automático

### Seguidor
- `POST /api/follower/update-amount` - Actualizar importe
- `POST /api/follower/start-bot` - Encender bot del seguidor
- `POST /api/follower/stop-bot` - Apagar bot del seguidor
- `GET /api/follower/bot-status` - Estado del bot

### Sistema
- `GET /api/status` - Estado general del sistema
- `POST /api/copytrading/manual` - Copytrading manual

## 🌐 WebSocket Events

### Eventos del Cliente
- `connect` - Conexión establecida
- `disconnect` - Conexión perdida
- `join_room` - Unirse a sala específica

### Eventos del Servidor
- `trader_connected` - Trader conectado
- `follower_connected` - Seguidor conectado
- `auto_copy_activated` - Copytrading automático activado
- `auto_copy_stopped` - Copytrading automático detenido
- `copytrading_result` - Resultado de operación

## 🎯 Flujo de Trabajo

### Para Traders
1. **Login** como Trader
2. **Conectar** cuenta ExNova
3. **Activar** copytrading automático
4. **Ejecutar** operaciones normalmente
5. **Monitorear** seguidores en tiempo real

### Para Seguidores
1. **Login** como Seguidor
2. **Conectar** cuenta ExNova
3. **Configurar** importe por operación
4. **Encender** bot de copytrading
5. **Recibir** operaciones automáticamente

## ⚙️ Configuración

### Variables de Entorno
```bash
# Puerto del servidor (opcional)
export PORT=5003

# Modo de debug (opcional)
export DEBUG=False
```

### Configuración de ExNova
- **Modo Demo**: Para pruebas sin riesgo
- **Modo Real**: Para operaciones con dinero real
- **Credenciales**: Email y contraseña de ExNova

## 🔧 Solución de Problemas

### Error de Conexión
```bash
# Verificar que el puerto 5003 esté libre
netstat -an | grep 5003

# Cambiar puerto si es necesario
python app.py --port 5004
```

### Error de Dependencias
```bash
# Reinstalar dependencias
pip install -r backend/requirements.txt --force-reinstall
```

### Error de Base de Datos
```bash
# Limpiar base de datos
rm -rf backend/database/*.json
```

## 📊 Monitoreo

### Logs del Sistema
- **Archivo**: `backend/copytrading_web.log`
- **Nivel**: INFO, WARNING, ERROR
- **Rotación**: Automática

### Métricas Disponibles
- Número de traders conectados
- Número de seguidores activos
- Estado de copytrading automático
- Operaciones ejecutadas

## 🛡️ Seguridad

### Medidas Implementadas
- **Validación de entrada**: Todos los inputs son validados
- **Gestión de sesiones**: Control de acceso por usuario
- **CORS configurado**: Acceso controlado desde frontend
- **Logs de auditoría**: Registro de todas las operaciones

## 🚀 Próximas Mejoras

- [ ] Panel de administración avanzado
- [ ] Métricas y estadísticas detalladas
- [ ] Sistema de notificaciones por email
- [ ] API de terceros para integraciones
- [ ] Modo multi-trader
- [ ] Sistema de comisiones

## 📞 Soporte

### Documentación
- Este README contiene toda la información necesaria
- Los logs del sistema proporcionan información detallada
- La consola del navegador muestra errores del frontend

### Contacto
- **Issues**: Reportar problemas en el repositorio
- **Logs**: Revisar `backend/copytrading_web.log`
- **Debug**: Activar modo debug para más información

## 📄 Licencia

Este proyecto es de uso interno y está diseñado específicamente para Metabinario.

---

**¡Metabinario Web Bot está listo para usar! 🚀**

Inicia el bot con `python start_web_bot.py` y accede a http://localhost:5003