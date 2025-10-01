#!/usr/bin/env python3
"""
Script de prueba para Metabinario Web Bot
Verifica que todos los componentes estén funcionando correctamente
"""

import requests
import json
import time
import sys

def test_backend_connection():
    """Probar conexión con el backend"""
    print("🔍 Probando conexión con el backend...")
    
    try:
        response = requests.get("http://localhost:5003/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend conectado correctamente")
            return True
        else:
            print(f"❌ Backend respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al backend. ¿Está ejecutándose?")
        return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_frontend_access():
    """Probar acceso al frontend"""
    print("🔍 Probando acceso al frontend...")
    
    try:
        response = requests.get("http://localhost:5003/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accesible correctamente")
            return True
        else:
            print(f"❌ Frontend respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede acceder al frontend")
        return False
    except Exception as e:
        print(f"❌ Error accediendo al frontend: {e}")
        return False

def test_api_endpoints():
    """Probar endpoints de la API"""
    print("🔍 Probando endpoints de la API...")
    
    endpoints = [
        ("/api/login", "POST"),
        ("/api/trader/status", "GET"),
        ("/api/follower/register", "POST"),
        ("/api/status", "GET")
    ]
    
    results = []
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://localhost:5003{endpoint}", timeout=5)
            else:
                response = requests.post(f"http://localhost:5003{endpoint}", 
                                       json={}, timeout=5)
            
            if response.status_code in [200, 401, 400]:  # 401 y 400 son respuestas válidas para endpoints protegidos
                print(f"✅ {endpoint} ({method}) - OK")
                results.append(True)
            else:
                print(f"❌ {endpoint} ({method}) - Código: {response.status_code}")
                results.append(False)
                
        except Exception as e:
            print(f"❌ {endpoint} ({method}) - Error: {e}")
            results.append(False)
    
    return all(results)

def test_database_files():
    """Probar archivos de base de datos"""
    print("🔍 Probando archivos de base de datos...")
    
    import os
    
    db_files = [
        "backend/database/followers.json",
        "backend/database/operations.json"
    ]
    
    results = []
    
    for file_path in db_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    json.load(f)
                print(f"✅ {file_path} - OK")
                results.append(True)
            except json.JSONDecodeError:
                print(f"❌ {file_path} - JSON inválido")
                results.append(False)
        else:
            print(f"⚠️ {file_path} - No existe (se creará automáticamente)")
            results.append(True)  # No es un error crítico
    
    return all(results)

def main():
    """Función principal de prueba"""
    print("🧪 Metabinario Web Bot - Test de Integración")
    print("=" * 50)
    
    tests = [
        ("Conexión Backend", test_backend_connection),
        ("Acceso Frontend", test_frontend_access),
        ("Endpoints API", test_api_endpoints),
        ("Archivos Base de Datos", test_database_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)  # Pausa entre pruebas
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El bot está listo para usar.")
        print("🌐 Accede a: http://localhost:5003")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

