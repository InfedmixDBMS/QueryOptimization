import os
import sys

#set path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_MANAGER_PATH = os.path.abspath(
    os.path.join(PROJECT_ROOT, '../StorageManager')
)

# add to python path
if STORAGE_MANAGER_PATH not in sys.path:
    sys.path.insert(0, STORAGE_MANAGER_PATH)

# set paths
STATS_PATH = os.path.join(STORAGE_MANAGER_PATH, 'storage/stats')
DATA_PATH = os.path.join(STORAGE_MANAGER_PATH, 'storage/data')
CATALOG_PATH = os.path.join(STORAGE_MANAGER_PATH, 'storage/catalog.json')

def verify_storage_manager():
    """
    Verifying StorageManager is accessib
    """
    if not os.path.exists(STORAGE_MANAGER_PATH):
        raise FileNotFoundError(
            f"StorageManager not found at {STORAGE_MANAGER_PATH}\n"
            #change the path if not same
            f"Expected location: ../StorageManager relative to QueryOptimization"
        )
    return True

def get_storage_info():
    """Get StorageManager paths"""
    return {
        'storage_manager_path': STORAGE_MANAGER_PATH,
        'stats_path': STATS_PATH,
        'data_path': DATA_PATH,
        'catalog_path': CATALOG_PATH,
        'exists': os.path.exists(STORAGE_MANAGER_PATH)
    }
