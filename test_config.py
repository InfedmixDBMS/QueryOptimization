import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import verify_storage_manager, get_storage_info

try:
    verify_storage_manager()
    info = get_storage_info()
    
    print(f"Path: {info['storage_manager_path']}")
    print(f"Stats Path: {info['stats_path']}")
    print(f"Exists: {info['exists']}")
    
except FileNotFoundError as e:
    print(f"fail: {e}")
    sys.exit(1)
