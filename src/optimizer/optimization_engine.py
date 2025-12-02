"""
Optimization Engine Module - Main interface for query optimization
"""

from ..parser.parser import Parser
from ..parser.validator import QueryValidator
from .plan_optimizer import PlanOptimizer
from .cost_calculator import CostCalculator

class OptimizationEngine:
    def __init__(self):
        """Initialize the optimization engine"""
        self.parser = Parser()
        self.validator = QueryValidator()
        self.plan_optimizer = PlanOptimizer()
        self.cost_calculator = CostCalculator()

    def parse_query(self, query: str):
        """Parse and validate SQL query string"""
        # 1. Parse query
        parsed_query = self.parser.parse_query(query)
        
        # 2. Validate parsed query
        is_valid, errors = self.validator.validate_parsed_query(parsed_query)
        if not is_valid:
            raise ValueError(f"Query validation failed: {errors}")
        
        return parsed_query

    def optimize_query(self, parsed_query):
        """Optimize parsed query using rules"""
        return self.plan_optimizer.optimize_tree(parsed_query)

    def optimize_query_with_genetic_algorithm(self, parsed_query, population_size=10, iterations=20, mutation_rate=0.3):
        """Optimize parsed query using genetic algorithm"""
        return self.plan_optimizer.optimize_tree_with_genetic_algorithm(parsed_query, population_size=population_size, iterations=iterations, mutation_rate=mutation_rate
        )

    def get_cost(self, parsed_query):
        """Calculate execution cost"""
        return self.cost_calculator.get_cost(parsed_query)