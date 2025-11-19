"""
Query Validator - Validates parsed queries
"""

class QueryValidator:
    def validate_parsed_query(self, parsed_query):
        """Validate a parsed query for correctness"""
        errors = []
        
        # 1. Cek komponen
        if not parsed_query.query_tree:
            errors.append("Missing query tree")
        
        # 2. Cek tabel
        if not parsed_query.tables:
            errors.append("No tables found in query")
        
        # 3. Validasi Struktur
        tree_errors = self._validate_tree_structure(parsed_query.query_tree)
        errors.extend(tree_errors)
        
        return len(errors) == 0, errors

    def _validate_tree_structure(self, node, visited=None):
        """Validate tree structure for cycles and correctness"""
        if visited is None:
            visited = set()
        
        errors = []
        
        # Cek Cycles
        if id(node) in visited:
            errors.append("Cycle detected in query tree")
            return errors
        
        visited.add(id(node))
        
        # Validate node type
        if not hasattr(node, 'type') or not node.type:
            errors.append("Node missing type")
        
        # Validate chidlren
        if hasattr(node, 'childs'):
            for child in node.childs:
                child_errors = self._validate_tree_structure(child, visited.copy())
                errors.extend(child_errors)
        
        return errors