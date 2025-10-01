# ExNova API Package
# Este archivo hace que exnovaapi sea un paquete Python importable

__version__ = "1.0.0"
__author__ = "MetaBot Team"

# Importar las clases principales para facilitar el uso
try:
    from .stable_api import Exnova
    from .api import ExnovaAPI
except ImportError as e:
    print(f"Warning: Error importing ExNova modules: {e}")
    Exnova = None
    ExnovaAPI = None