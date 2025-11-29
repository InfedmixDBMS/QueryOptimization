from src.config import verify_storage_manager
from classes.API import StorageEngine
from classes.DataModels import Statistic

verify_storage_manager()

class StorageAdapter:
    def __init__(self):
        """
        Adapter to storage_manager
        """
        pass
        
    def get_table_statistics(self, table_name):
        stats = StorageEngine.get_stats(table_name)
        
        return {
            'n_r': stats.n_r,
            'b_r': stats.b_r,
            'l_r': stats.l_r,
            'f_r': stats.f_r,
            'distinct_values': getattr(stats, 'V_a_r', {})
        }
    
    def update_statistics(self, table_name):
        StorageEngine.update_stats(table_name)
        print(f"Statistics updated for : {table_name}")

    @property
    def is_available(self) -> bool:
        return self.use_real_storage