# 🤖 Bot de Trading Web

Sistema de Copytrading Web profesional desplegado en Railway.

## 🚀 Características

- ✅ **Interfaz web moderna** y responsive
- ✅ **Sistema de roles** (Trader/Seguidor)
- ✅ **Autorización de usuarios** por email
- ✅ **WebSocket en tiempo real** para operaciones
- ✅ **Panel de administración** para traders
- ✅ **Base de datos JSON** simple y eficiente
- ✅ **Deploy automático** en Railway

## 📋 Usuarios por defecto

- **Trader Principal**: `binariosector91@outlook.com`
- **Seguidor Autorizado**: `clickrealbinarias@outlook.com`

## 🛠️ Instalación Local

1. **Clonar el repositorio**:
```bash
git clone <tu-repositorio>
cd railway_bot
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Ejecutar localmente**:
```bash
python app.py
```

4. **Abrir en el navegador**:
```
http://localhost:5000
```

## ☁️ Deploy en Railway

1. **Crear cuenta en Railway**:
   - Ve a [railway.app](https://railway.app)
   - Regístrate con GitHub

2. **Conectar repositorio**:
   - Conecta tu repositorio de GitHub
   - Railway detectará automáticamente los archivos

3. **Deploy automático**:
   - Railway desplegará automáticamente
   - Obtendrás una URL permanente

## 🔧 Configuración

### Variables de entorno (opcional):
- `SECRET_KEY`: Clave secreta para Flask
- `PORT`: Puerto del servidor (Railway lo asigna automáticamente)

### Base de datos:
- Los archivos JSON se crean automáticamente
- Ubicación: `database/`
- Archivos: `authorized_users.json`, `followers.json`

## 📱 Uso

1. **Acceder a la URL** de Railway
2. **Seleccionar rol** (Trader o Seguidor)
3. **Iniciar sesión** con email autorizado
4. **Usar el panel** según tu rol

## 🔒 Seguridad

- Solo emails autorizados pueden acceder
- El trader puede gestionar usuarios
- WebSocket seguro con CORS configurado
- Validación de roles en todas las rutas

## 📊 API Endpoints

- `GET /` - Página principal
- `POST /api/login` - Iniciar sesión
- `GET /api/status` - Estado del bot
- `GET /api/admin/authorized-users` - Lista de usuarios (solo trader)
- `POST /api/admin/add-user` - Agregar usuario (solo trader)

## 🚀 Ventajas de Railway

- ✅ **Gratis** para empezar
- ✅ **URL permanente** que nunca cambia
- ✅ **Deploy automático** desde GitHub
- ✅ **Escalable** según necesidades
- ✅ **Sin configuración** compleja
- ✅ **Soporte completo** para Flask + SocketIO

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Railway
2. Verifica que los archivos estén correctos
3. Asegúrate de que las dependencias estén instaladas

## 🎯 Próximos pasos

1. **Subir a GitHub** el código
2. **Conectar Railway** con GitHub
3. **Deploy automático** en Railway
4. **Compartir URL** con usuarios
5. **¡Disfrutar tu bot web!** 🎉
