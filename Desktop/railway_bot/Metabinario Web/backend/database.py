#!/usr/bin/env python3
"""
Database Manager para Metabinario Web Bot
Manejo simple de base de datos JSON para seguidores y operaciones
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class DatabaseManager:
    """Gestor de base de datos simple"""
    
    def __init__(self, db_dir="database"):
        self.db_dir = db_dir
        self.followers_file = os.path.join(db_dir, "followers.json")
        self.operations_file = os.path.join(db_dir, "operations.json")
        
        # Crear directorio si no existe
        os.makedirs(db_dir, exist_ok=True)
        
        # Inicializar archivos si no existen
        self._init_files()
    
    def _init_files(self):
        """Inicializar archivos de base de datos si no existen"""
        if not os.path.exists(self.followers_file):
            with open(self.followers_file, 'w', encoding='utf-8') as f:
                json.dump({"followers": []}, f, indent=2, ensure_ascii=False)
        
        if not os.path.exists(self.operations_file):
            with open(self.operations_file, 'w', encoding='utf-8') as f:
                json.dump({"operations": []}, f, indent=2, ensure_ascii=False)
    
    def get_follower_stats(self, email: str) -> Optional[Dict]:
        """Obtener estadísticas de un seguidor"""
        try:
            with open(self.followers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for follower in data.get("followers", []):
                if follower.get("email") == email:
                    return follower
            
            return None
        except Exception as e:
            print(f"Error obteniendo estadísticas del seguidor: {e}")
            return None
    
    def update_follower_amount(self, email: str, amount: float) -> bool:
        """Actualizar importe de un seguidor"""
        try:
            with open(self.followers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = False
            for follower in data.get("followers", []):
                if follower.get("email") == email:
                    follower["amount"] = amount
                    follower["updated_at"] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                with open(self.followers_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            
            return False
        except Exception as e:
            print(f"Error actualizando importe del seguidor: {e}")
            return False
    
    def add_operation(self, operation_data: Dict) -> bool:
        """Agregar una operación a la base de datos"""
        try:
            with open(self.operations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            operation_data["timestamp"] = datetime.now().isoformat()
            data["operations"].append(operation_data)
            
            with open(self.operations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error agregando operación: {e}")
            return False
    
    def get_recent_operations(self, limit: int = 50) -> List[Dict]:
        """Obtener operaciones recientes"""
        try:
            with open(self.operations_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            operations = data.get("operations", [])
            # Ordenar por timestamp descendente y limitar
            operations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return operations[:limit]
        except Exception as e:
            print(f"Error obteniendo operaciones recientes: {e}")
            return []

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()