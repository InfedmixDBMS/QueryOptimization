"""
Query Models - Simple data structures for query optimization
"""

class QueryTree:
    """Tree node for parsed queries"""
    def __init__(self, type: str, val: str):
        self.type = type
        self.val = val
        self.children = []

    def add_child(self, child):
        self.children.append(child)


class ParsedQuery:
    """Parsed SQL query representation"""
    def __init__(self, query: str, query_tree: QueryTree):
        self.query = query
        self.query_tree = query_tree
        self.is_optimized = False