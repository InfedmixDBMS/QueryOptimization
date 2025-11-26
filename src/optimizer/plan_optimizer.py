"""
Plan Optimizer Module - Applies optimization rules to query trees
"""

from .rules import OptimizationRules
from .cost_calculator import CostCalculator
from ..tree.parsed_query import ParsedQuery
import copy

class PlanOptimizer:
    def __init__(self):
        """Initialize plan optimizer with optimization rules"""
        self.rules = OptimizationRules()
        self.cost_calculator = CostCalculator()
    
    def optimize_tree(self, parsed_query):
        """
        Generate multiple query plans and select the best one based on cost
        
        Strategy:
        1. Generate multiple candidate plans using different rule orderings
        2. Calculate cost for each plan
        3. Select and return the plan with lowest cost
        """
        original_tree = parsed_query.query_tree
        
        print("\n" + "="*60)
        print("🔍 GENERATING MULTIPLE QUERY PLANS")
        print("="*60)
        candidate_plans = []
        
        # Plan 1: Selection-First Strategy (standard heuristic)
        plan1 = self._generate_selection_first_plan(copy.deepcopy(original_tree))
        candidate_plans.append(('Selection-First (Standard)', plan1))
        
        # Plan 2: Projection-First Strategy
        plan2 = self._generate_projection_first_plan(copy.deepcopy(original_tree))
        candidate_plans.append(('Projection-First', plan2))
        
        # Plan 3: Balanced Strategy (alternating)
        plan3 = self._generate_balanced_plan(copy.deepcopy(original_tree))
        candidate_plans.append(('Balanced (Alternating)', plan3))
        
        # Plan 4: Aggressive Combination
        plan4 = self._generate_aggressive_combination_plan(copy.deepcopy(original_tree))
        candidate_plans.append(('Aggressive Combination', plan4))
        
        # Plan 5: Conservative (minimal transformation)
        plan5 = self._generate_conservative_plan(copy.deepcopy(original_tree))
        candidate_plans.append(('Conservative (Minimal)', plan5))
        
        # Plan 6: Swap-Optimized Strategy
        plan6 = self._generate_swap_optimized_plan(copy.deepcopy(original_tree))
        candidate_plans.append(('Swap-Optimized (Rule 2)', plan6))
        
        print("\nCOST EVALUATION:")
        print("-" * 60)
        
        plan_results = []
        for plan_name, plan_tree in candidate_plans:
            cost = self.cost_calculator._calculate_tree_cost(plan_tree)
            plan_results.append((plan_name, plan_tree, cost))
            print(f"  {plan_name:30s} | Cost: {cost:8.2f}")
        
        # Select best plan (lowest cost)
        best_plan = min(plan_results, key=lambda x: x[2])
        best_name, best_tree, best_cost = best_plan
        
        print("-" * 60)
        print(f"SELECTED PLAN: {best_name}")
        print(f"Final Cost: {best_cost:.2f}")
        print("="*60 + "\n")
        return ParsedQuery(parsed_query.query, best_tree)
    
    def _generate_selection_first_plan(self, tree):
        """
        Strategy 1: Selection-First (Standard Heuristic)
        Priority: Reduce data size early via selections
        """
        tree = self.rules.push_down_selection(tree)
        tree = self.rules.swap_selection(tree) 
        tree = self.rules.combine_selections(tree)
        tree = self.rules.push_down_projection(tree)
        tree = self.rules.distribute_selection_over_join(tree)
        tree = self.rules.distribute_projection_over_join(tree)
        tree = self.rules.combine_cartesian_with_selection(tree)
        tree = self.rules.reorder_joins(tree)
        tree = self.rules.apply_associativity(tree)
        return tree
    
    def _generate_projection_first_plan(self, tree):
        """
        Strategy 2: Projection-First
        Priority: Reduce tuple width early via projections
        """
        tree = self.rules.push_down_projection(tree)
        tree = self.rules.distribute_projection_over_join(tree)
        tree = self.rules.push_down_selection(tree)
        tree = self.rules.combine_selections(tree)
        tree = self.rules.distribute_selection_over_join(tree)
        tree = self.rules.combine_cartesian_with_selection(tree)
        tree = self.rules.reorder_joins(tree)
        tree = self.rules.apply_associativity(tree)
        return tree
    
    def _generate_balanced_plan(self, tree):
        """
        Strategy 3: Balanced (Alternating)
        Priority: Balance between selection and projection push-down
        """
        tree = self.rules.push_down_selection(tree)
        tree = self.rules.swap_selection(tree)
        tree = self.rules.push_down_projection(tree)
        tree = self.rules.distribute_selection_over_join(tree)
        tree = self.rules.distribute_projection_over_join(tree)
        tree = self.rules.combine_selections(tree)
        tree = self.rules.combine_cartesian_with_selection(tree)
        tree = self.rules.reorder_joins(tree)
        tree = self.rules.apply_associativity(tree)
        return tree
    
    def _generate_aggressive_combination_plan(self, tree):
        """
        Strategy 4: Aggressive Combination
        Priority: Maximize rule application and combinations
        """
        # Multiple passes untuk optimasi agresif
        for _ in range(2):  
            tree = self.rules.push_down_selection(tree)
            tree = self.rules.push_down_projection(tree)
            tree = self.rules.combine_selections(tree)
        
        tree = self.rules.distribute_selection_over_join(tree)
        tree = self.rules.distribute_projection_over_join(tree)
        tree = self.rules.combine_cartesian_with_selection(tree)
        tree = self.rules.reorder_joins(tree)
        tree = self.rules.apply_associativity(tree)
        return tree
    
    def _generate_conservative_plan(self, tree):
        """
        Strategy 5: Conservative (Minimal Transformation)
        Priority: Apply only essential optimizations
        """
        tree = self.rules.push_down_selection(tree)
        tree = self.rules.combine_selections(tree)
        tree = self.rules.combine_cartesian_with_selection(tree)
        return tree
    
    def _generate_swap_optimized_plan(self, tree):
        """
        Strategy 6: Swap-Optimized Aggressively reorder selections for better performance
        """
        tree = self.rules.push_down_selection(tree)
        tree = self.rules.swap_selection(tree)
        tree = self.rules.combine_selections(tree)
        tree = self.rules.push_down_projection(tree)
        tree = self.rules.distribute_selection_over_join(tree)
        tree = self.rules.distribute_projection_over_join(tree)
        tree = self.rules.combine_cartesian_with_selection(tree)
        tree = self.rules.reorder_joins(tree)
        tree = self.rules.apply_associativity(tree)
        
        return tree