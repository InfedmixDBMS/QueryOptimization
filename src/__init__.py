"""
Query Optimizer Component for mDBMS

This package implements the Query Optimizer component responsible for:
- Parsing SQL queries
- Optimizing query execution plans
- Calculating query execution costs
"""

from .query_models import ParsedQuery, QueryTree
from .optimization_engine import OptimizationEngine
from .cost_calculator import get_cost

__version__ = "1.0.0"
__author__ = "Q#"

__all__ = [
    'ParsedQuery',
    'QueryTree',
    'OptimizationEngine',
    'get_cost'
]