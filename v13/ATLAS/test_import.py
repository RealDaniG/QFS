import sys
import os

print("Testing imports...")
try:
    print("Importing config...")
    from src import config

    print("Config imported.")

    print("Importing models...")
    from src.api import models

    print("Models imported.")

    print("Importing dependencies...")
    from src.api import dependencies

    print("Dependencies imported.")

    print("Importing cycles...")
    from src.lib import cycles

    print("Cycles imported.")

    print("Importing storage...")
    from src.lib import storage

    print("Storage imported.")

    print("Importing auth...")
    from src.api.routes import auth

    print("Auth imported.")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
