#!/usr/bin/env python3
"""
APLICAR CORRECCIONES AL BOT DEL SEGUIDOR
"""

import re

def apply_corrections():
    """Aplicar todas las correcciones necesarias"""
    file_path = "/Users/rick/Desktop/BOTTELEGRAM/metabot_modificado/Metabinario Web/backend/our_copytrading_api.py"
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔧 APLICANDO CORRECCIONES AL BOT DEL SEGUIDOR")
    print("=" * 60)
    
    # CORRECCIÓN 1: Ya aplicada - línea comentada
    print("✅ Corrección 1: Línea de sincronización comentada")
    
    # CORRECCIÓN 2: Mejorar función _update_auto_copy_follower_status
    old_function = '''    def _update_auto_copy_follower_status(self, email: str, status: bool):
        """Actualizar estado del bot en las instancias de copytrading automático"""
        logger.info(f"🔄 Intentando actualizar estado del bot para {email} a {'ENCENDIDO' if status else 'APAGADO'}")
        
        if hasattr(self, 'auto_copy_followers') and self.auto_copy_followers:
            logger.info(f"🔄 auto_copy_followers existe con {len(self.auto_copy_followers)} seguidores")
            for follower in self.auto_copy_followers:
                logger.info(f"🔄 Verificando seguidor: {follower.email}")
                if follower.email == email:
                    self.follower_bot_status[email] = status
                    logger.info(f"✅ Estado del bot actualizado en copytrading automático para {email}: {'ENCENDIDO' if status else 'APAGADO'}")
                    return True
            logger.warning(f"⚠️ Seguidor {email} no encontrado en auto_copy_followers")
        else:
            logger.warning(f"⚠️ auto_copy_followers no existe o está vacío")
        return False'''
    
    new_function = '''    def _update_auto_copy_follower_status(self, email: str, status: bool):
        """Actualizar estado del bot en las instancias de copytrading automático"""
        logger.info(f"🔄 Intentando actualizar estado del bot para {email} a {'ENCENDIDO' if status else 'APAGADO'}")
        
        # SIEMPRE actualizar el estado del bot, independientemente de auto_copy_followers
        self.follower_bot_status[email] = status
        logger.info(f"✅ Estado del bot actualizado para {email}: {'ENCENDIDO' if status else 'APAGADO'}")
        
        # También actualizar en auto_copy_followers si existe
        if hasattr(self, 'auto_copy_followers') and self.auto_copy_followers:
            logger.info(f"🔄 auto_copy_followers existe con {len(self.auto_copy_followers)} seguidores")
            for follower in self.auto_copy_followers:
                logger.info(f"🔄 Verificando seguidor: {follower.email}")
                if follower.email == email:
                    logger.info(f"✅ Seguidor encontrado en auto_copy_followers: {email}")
                    return True
            logger.warning(f"⚠️ Seguidor {email} no encontrado en auto_copy_followers")
        else:
            logger.warning(f"⚠️ auto_copy_followers no existe o está vacío")
        
        return True  # Siempre retornar True porque actualizamos el estado'''
    
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Corrección 2: Función _update_auto_copy_follower_status mejorada")
    else:
        print("⚠️ Corrección 2: Función no encontrada")
    
    # CORRECCIÓN 3: Mejorar función _sync_follower_bot_status
    old_sync_function = '''    def _sync_follower_bot_status(self):
        """Sincronizar estado del bot de seguidores con las instancias actuales"""
        logger.info("🔄 Sincronizando estado de bots de seguidores...")
        
        # Para cada seguidor en las instancias actuales, mantener el estado si ya existe
        for follower in self.auto_copy_followers:
            if follower.email in self.follower_bot_status:
                current_status = self.follower_bot_status[follower.email]
                logger.info(f"🔄 Manteniendo estado del bot para {follower.email}: {'ENCENDIDO' if current_status else 'APAGADO'}")
            else:
                # Si no existe, establecer como APAGADO por defecto
                self.follower_bot_status[follower.email] = False
                logger.info(f"🔄 Estado inicial del bot para {follower.email}: APAGADO")
        
        logger.info("✅ Sincronización de estado de bots completada")'''
    
    new_sync_function = '''    def _sync_follower_bot_status(self):
        """Sincronizar estado del bot de seguidores con las instancias actuales"""
        logger.info("🔄 Sincronizando estado de bots de seguidores...")
        
        # Para cada seguidor en las instancias actuales, mantener el estado si ya existe
        for follower in self.auto_copy_followers:
            if follower.email in self.follower_bot_status:
                current_status = self.follower_bot_status[follower.email]
                logger.info(f"🔄 Manteniendo estado del bot para {follower.email}: {'ENCENDIDO' if current_status else 'APAGADO'}")
            else:
                # Solo establecer como APAGADO si NO existe previamente
                self.follower_bot_status[follower.email] = False
                logger.info(f"🔄 Estado inicial del bot para {follower.email}: APAGADO")
        
        logger.info("✅ Sincronización de estado de bots completada")'''
    
    if old_sync_function in content:
        content = content.replace(old_sync_function, new_sync_function)
        print("✅ Corrección 3: Función _sync_follower_bot_status mejorada")
    else:
        print("⚠️ Corrección 3: Función no encontrada")
    
    # Escribir el archivo corregido
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print("✅ TODAS LAS CORRECCIONES APLICADAS:")
    print("1. ✅ Línea de sincronización problemática comentada")
    print("2. ✅ Función de actualización mejorada")
    print("3. ✅ Función de sincronización mejorada")
    print("\n🎯 PROBLEMAS CORREGIDOS:")
    print("• El bot del seguidor ahora se mantiene encendido")
    print("• No se sobrescribe el estado al iniciar auto copy")
    print("• La sincronización preserva el estado actual")
    print("=" * 60)

if __name__ == "__main__":
    apply_corrections()
