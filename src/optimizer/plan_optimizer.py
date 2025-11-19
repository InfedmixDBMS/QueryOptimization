"""
Plan Optimizer Module - Applies optimization rules to query trees
"""

from .rules import OptimizationRules
from ..tree.parsed_query import ParsedQuery

class PlanOptimizer:
    def __init__(self):
        """Initialize plan optimizer with optimization rules"""
        self.rules = OptimizationRules()

    def optimize_tree(self, parsed_query):
        """
        Apply optimization rules to parsed query tree
        """
        # Get the original tree
        original_tree = parsed_query.query_tree
        optimized_tree = original_tree
        
        # Apply rules in order (sesuai spesifikasi)
        print("Applying optimization rules...")
        
        # 1. Push down selections
        optimized_tree = self.rules.push_down_selection(optimized_tree)
        print("Push down selection applied")
        
        # 2. Push down projections  
        optimized_tree = self.rules.push_down_projection(optimized_tree)
        print("Push down projection applied")
        
        # 3. Combine selections
        optimized_tree = self.rules.combine_selections(optimized_tree)
        print("Combine selections applied")
        
        # 4. Convert Cartesian products to joins
        optimized_tree = self.rules.combine_cartesian_with_selection(optimized_tree)
        print("Cartesian to join conversion applied")
        
        # 5. Reorder joins
        optimized_tree = self.rules.reorder_joins(optimized_tree)
        print("Join reordering applied")

        # 6. Apply associativity
        optimized_tree = self.rules.apply_associativity(optimized_tree)
        print("Join associativity applied")

        # 7. Distribute selection over join
        optimized_tree = self.rules.distribute_selection_over_join(optimized_tree)
        print("Selection distribution over join applied")

        # 8. Distribute projection over join
        optimized_tree = self.rules.distribute_projection_over_join(optimized_tree)
        print("Projection distribution over join applied")
        
        # Return optiimzed parsed query
        optimized_parsed_query = ParsedQuery(parsed_query.query, optimized_tree)
        return optimized_parsed_query