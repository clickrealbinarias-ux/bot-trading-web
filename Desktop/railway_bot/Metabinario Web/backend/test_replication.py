#!/usr/bin/env python3
"""
SCRIPT DE PRUEBA DE REPLICACIÓN
Simula operaciones para probar la replicación del bot web
"""

import sys
import os
import time
import json
import logging
import requests
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class ReplicationTester:
    """Tester de replicación del bot web"""
    
    def __init__(self):
        self.web_base_url = "http://localhost:5003"
        self.session = requests.Session()
        
    def test_login_trader(self, email, password, balance_mode="PRACTICE"):
        """Probar login como trader"""
        try:
            logger.info(f"🔐 Probando login como trader: {email}")
            
            response = self.session.post(f"{self.web_base_url}/api/login", json={
                "email": email,
                "password": password,
                "role": "trader",
                "balance_mode": balance_mode
            })
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Login trader exitoso: {data}")
                return True
            else:
                logger.error(f"❌ Error en login trader: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción en login trader: {e}")
            return False
    
    def test_login_follower(self, email, password, balance_mode="PRACTICE", amount=10.0):
        """Probar login como seguidor"""
        try:
            logger.info(f"🔐 Probando login como seguidor: {email}")
            
            response = self.session.post(f"{self.web_base_url}/api/login", json={
                "email": email,
                "password": password,
                "role": "follower",
                "balance_mode": balance_mode,
                "amount": amount
            })
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Login seguidor exitoso: {data}")
                return True
            else:
                logger.error(f"❌ Error en login seguidor: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción en login seguidor: {e}")
            return False
    
    def test_start_auto_copy(self):
        """Probar activar auto copy"""
        try:
            logger.info("🤖 Probando activar auto copy...")
            
            response = self.session.post(f"{self.web_base_url}/api/trader/start-auto-copy")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Auto copy activado: {data}")
                return True
            else:
                logger.error(f"❌ Error activando auto copy: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción activando auto copy: {e}")
            return False
    
    def test_start_follower_bot(self, email):
        """Probar activar bot del seguidor"""
        try:
            logger.info(f"🤖 Probando activar bot del seguidor: {email}")
            
            response = self.session.post(f"{self.web_base_url}/api/follower/start-bot", json={
                "email": email
            })
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Bot del seguidor activado: {data}")
                return True
            else:
                logger.error(f"❌ Error activando bot del seguidor: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción activando bot del seguidor: {e}")
            return False
    
    def test_manual_operation(self, amount, active, direction, duration):
        """Probar operación manual"""
        try:
            logger.info(f"📈 Probando operación manual: {active} {direction} ${amount}")
            
            response = self.session.post(f"{self.web_base_url}/api/copytrading/manual", json={
                "amount": amount,
                "active": active,
                "direction": direction,
                "duration": duration
            })
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Operación manual exitosa: {data}")
                return True
            else:
                logger.error(f"❌ Error en operación manual: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción en operación manual: {e}")
            return False
    
    def get_status(self):
        """Obtener estado del sistema"""
        try:
            response = self.session.get(f"{self.web_base_url}/api/status")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Error obteniendo estado: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Excepción obteniendo estado: {e}")
            return None
    
    def test_web_connection(self):
        """Probar conexión básica con el bot web"""
        try:
            logger.info("🌐 Probando conexión con el bot web...")
            response = self.session.get(f"{self.web_base_url}/")
            if response.status_code == 200:
                logger.info("✅ Bot web responde correctamente")
                return True
            else:
                logger.error(f"❌ Bot web respondió con código {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ No se pudo conectar con el bot web: {e}")
            return False
    
    def run_full_test(self):
        """Ejecutar prueba completa"""
        logger.info("🚀 Iniciando prueba completa de replicación")
        logger.info("=" * 60)
        
        # 1. Verificar que el bot web esté activo
        logger.info("1️⃣ Verificando que el bot web esté activo...")
        if not self.test_web_connection():
            logger.error("❌ El bot web no está activo")
            return False
        
        logger.info("✅ Bot web activo")
        
        # 2. Login como trader
        logger.info("2️⃣ Haciendo login como trader...")
        trader_success = self.test_login_trader(
            "binariosector91@outlook.com",
            "Galileatrade27$",
            "PRACTICE"
        )
        
        if not trader_success:
            logger.error("❌ No se pudo hacer login como trader")
            return False
        
        # 3. Login como seguidor
        logger.info("3️⃣ Haciendo login como seguidor...")
        follower_success = self.test_login_follower(
            "clickrealbinarias@outlook.com",
            "Galileatrade27$",
            "PRACTICE",
            15.0
        )
        
        if not follower_success:
            logger.error("❌ No se pudo hacer login como seguidor")
            return False
        
        # 4. Activar bot del seguidor
        logger.info("4️⃣ Activando bot del seguidor...")
        bot_success = self.test_start_follower_bot("clickrealbinarias@outlook.com")
        
        if not bot_success:
            logger.error("❌ No se pudo activar bot del seguidor")
            return False
        
        # 5. Activar auto copy
        logger.info("5️⃣ Activando auto copy...")
        auto_copy_success = self.test_start_auto_copy()
        
        if not auto_copy_success:
            logger.error("❌ No se pudo activar auto copy")
            return False
        
        # 6. Probar operación manual
        logger.info("6️⃣ Probando operación manual...")
        operation_success = self.test_manual_operation(
            10.0,
            "EURUSD",
            "CALL",
            2
        )
        
        if not operation_success:
            logger.error("❌ No se pudo ejecutar operación manual")
            return False
        
        # 7. Verificar estado final
        logger.info("7️⃣ Verificando estado final...")
        final_status = self.get_status()
        if final_status:
            logger.info(f"📊 Estado final: {json.dumps(final_status, indent=2)}")
        
        logger.info("✅ Prueba completa finalizada")
        return True

def main():
    """Función principal"""
    logger.info("🧪 INICIANDO PRUEBA DE REPLICACIÓN")
    logger.info("=" * 60)
    
    tester = ReplicationTester()
    
    # Ejecutar prueba completa
    success = tester.run_full_test()
    
    if success:
        logger.info("🎉 PRUEBA EXITOSA")
    else:
        logger.error("💥 PRUEBA FALLIDA")
    
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
