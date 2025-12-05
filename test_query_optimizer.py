import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.optimizer.optimization_engine import OptimizationEngine
from src.tree.nodes import NodeType


class TestQueryOptimizer(unittest.TestCase):
    """Unit tests for Query Optimizer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.optimizer = OptimizationEngine(use_real_storage=False)
    
    def test_case_1_simple_selection_optimization(self):
        """
        TEST CASE 1: Simple Selection with Single Table
        """
        print("\n" + "="*80)
        print("TEST CASE 1: Simple Selection with Single Table")
        print("="*80)

        query = "SELECT emp.name, emp.salary FROM employees emp WHERE emp.salary > 50000"
        print(f"\nInput Query:\n{query}")

        print("\n[Step 1] Parsing query...")
        parsed_query = self.optimizer.parse_query(query)
        
        # Assertions buat parsed query
        self.assertIsNotNone(parsed_query, "Parsed query should not be None")
        self.assertIsNotNone(parsed_query.query_tree, "Query tree should not be None")
        self.assertEqual(len(parsed_query.tables), 1, "Should have exactly 1 table")
        self.assertIn('employees', parsed_query.tables, "Should contain 'employees' table")
        
        print(f"Query parsed successfully")
        print(f"Tables identified: {parsed_query.tables}")

        print("\n[Step 2] Validating query tree structure...")
        root = parsed_query.query_tree
        
        self.assertEqual(root.type, NodeType.PROJECT.value, "Root should be PROJECT node")
        self.assertTrue(len(root.childs) > 0, "PROJECT should have children")
        
        # Check SELECT node
        select_node = root.childs[0]
        self.assertEqual(select_node.type, NodeType.SELECT.value, "First child should be SELECT node")
        
        # Check TABLE node
        self.assertTrue(len(select_node.childs) > 0, "SELECT should have children")
        table_node = select_node.childs[0]
        self.assertEqual(table_node.type, NodeType.TABLE.value, "Should have TABLE node")
        self.assertEqual(table_node.val, 'employees', "Table name should be 'employees'")
        
        print("Tree structure validated: PROJECT -> SELECT -> TABLE")
        print("\nOriginal Query Tree:")
        parsed_query.print_tree()

        print("\n[Step 3] Calculating original query cost...")
        original_cost = self.optimizer.get_cost(parsed_query)
        
        self.assertIsNotNone(original_cost, "Cost should not be None")
        self.assertGreaterEqual(original_cost, 0, "Cost should be non-negative")
        
        print(f"Original cost calculated: {original_cost:.2f}")

        print("\n[Step 4] Optimizing query...")
        optimized_query = self.optimizer.optimize_query(parsed_query)
        
        self.assertIsNotNone(optimized_query, "Optimized query should not be None")
        self.assertIsNotNone(optimized_query.query_tree, "Optimized tree should not be None")
        
        print("\nOptimized Query Tree:")
        optimized_query.print_tree()

        print("\n[Step 5] Calculating optimized query cost...")
        optimized_cost = self.optimizer.get_cost(optimized_query)
        
        self.assertIsNotNone(optimized_cost, "Optimized cost should not be None")
        self.assertGreaterEqual(optimized_cost, 0, "Optimized cost should be non-negative")
        self.assertLessEqual(optimized_cost, original_cost, 
                            "Optimized cost should be <= original cost")
        
        print(f"Optimized cost calculated: {optimized_cost:.2f}")

        print("\n[Step 6] Verifying semantic equivalence...")
        self.assertEqual(set(parsed_query.tables), set(optimized_query.tables),
                        "Tables should remain the same after optimization")
        
        print("Semantic equivalence maintained")
        
        # Summary
        print("\n" + "="*80)
        print("TEST CASE 1 RESULTS")
        print("="*80)
        print(f"Status: PASSED")
        print(f"Tables: {parsed_query.tables}")
        print(f"Original Cost: {original_cost:.2f}")
        print(f"Optimized Cost: {optimized_cost:.2f}")
        print(f"Cost Improvement: {((original_cost - optimized_cost) / original_cost * 100):.2f}%")
        print("="*80 + "\n")
    
    def test_case_2_join_optimization_multiple_tables(self):
        """
        TEST CASE 2: JOIN Optimization with Multiple Tables
        """
        print("\n" + "="*80)
        print("TEST CASE 2: JOIN Optimization with Multiple Tables")
        print("="*80)

        query = """
        SELECT s.name, d.dept_name, p.project_name 
        FROM students s 
        JOIN departments d ON s.dept_id = d.id 
        JOIN projects p ON s.project_id = p.id 
        WHERE s.age > 20 AND d.budget > 100000
        """
        print(f"\nInput Query:\n{query}")

        print("\n[Step 1] Parsing complex query with JOINs...")
        parsed_query = self.optimizer.parse_query(query)
        
        # Assertions buat parsed query
        self.assertIsNotNone(parsed_query, "Parsed query should not be None")
        self.assertIsNotNone(parsed_query.query_tree, "Query tree should not be None")
        self.assertEqual(len(parsed_query.tables), 3, "Should have exactly 3 tables")
        
        expected_tables = {'students', 'departments', 'projects'}
        self.assertEqual(set(parsed_query.tables), expected_tables, 
                        f"Should contain tables: {expected_tables}")
        
        print(f"Query parsed successfully")
        print(f"Tables identified: {parsed_query.tables}")
  
        print("\n[Step 2] Validating JOIN tree structure...")
        root = parsed_query.query_tree
        
        self.assertEqual(root.type, NodeType.PROJECT.value, "Root should be PROJECT node")
        self.assertTrue(len(root.childs) > 0, "PROJECT should have children")
        
        # Check for SELECT node (WHERE clause)
        select_node = root.childs[0]
        self.assertEqual(select_node.type, NodeType.SELECT.value, 
                        "First child should be SELECT node (WHERE clause)")
        
        # Verify SELECT has JOIN children
        self.assertTrue(len(select_node.childs) > 0, "SELECT should have children")
        
        # Check for JOIN nodes
        join_count = 0
        def count_joins(node):
            nonlocal join_count
            if node.type == NodeType.JOIN.value:
                join_count += 1
            for child in node.childs:
                count_joins(child)
        
        count_joins(root)
        self.assertGreaterEqual(join_count, 2, "Should have at least 2 JOIN nodes")
        
        print(f"Tree structure validated with {join_count} JOIN nodes")
        print("\nOriginal Query Tree:")
        parsed_query.print_tree()

        print("\n[Step 3] Calculating original query cost...")
        original_cost = self.optimizer.get_cost(parsed_query)
        
        self.assertIsNotNone(original_cost, "Cost should not be None")
        self.assertGreaterEqual(original_cost, 0, "Cost should be non-negative")
        
        print(f"Original cost calculated: {original_cost:.2f}")

        print("\n[Step 4] Optimizing query with multiple plan generation...")
        optimized_query = self.optimizer.optimize_query(parsed_query)
        
        self.assertIsNotNone(optimized_query, "Optimized query should not be None")
        self.assertIsNotNone(optimized_query.query_tree, "Optimized tree should not be None")
        
        print("\nOptimized Query Tree:")
        optimized_query.print_tree()

        print("\n[Step 5] Validating optimized tree structure...")
        opt_root = optimized_query.query_tree
        
        # Check root PROJECT
        self.assertEqual(opt_root.type, NodeType.PROJECT.value, 
                        "Optimized root should still be PROJECT")

        table_count = 0
        def count_tables(node):
            nonlocal table_count
            if node.type == NodeType.TABLE.value:
                table_count += 1
            for child in node.childs:
                count_tables(child)
        
        count_tables(opt_root)
        self.assertEqual(table_count, 3, "Should still have 3 tables after optimization")
        
        print("Optimized tree structure validated")

        print("\n[Step 6] Calculating optimized query cost...")
        optimized_cost = self.optimizer.get_cost(optimized_query)
        
        self.assertIsNotNone(optimized_cost, "Optimized cost should not be None")
        self.assertGreaterEqual(optimized_cost, 0, "Optimized cost should be non-negative")
        self.assertLessEqual(optimized_cost, original_cost * 1.1,  # 10% toleransi
                            "Optimized cost should not be significantly worse")
        
        print(f"Optimized cost calculated: {optimized_cost:.2f}")

        print("\n[Step 7] Verifying semantic equivalence...")
        self.assertEqual(set(parsed_query.tables), set(optimized_query.tables),
                        "Tables should remain the same after optimization")
        
        print("Semantic equivalence maintained - all tables preserved")
        
        # SUmmary
        print("\n" + "="*80)
        print("TEST CASE 2 RESULTS")
        print("="*80)
        print(f"Status: PASSED")
        print(f"Tables: {parsed_query.tables}")
        print(f"JOIN Operations: {join_count}")
        print(f"Original Cost: {original_cost:.2f}")
        print(f"Optimized Cost: {optimized_cost:.2f}")
        
        if optimized_cost < original_cost:
            improvement = ((original_cost - optimized_cost) / original_cost * 100)
            print(f"Cost Improvement: {improvement:.2f}%")
        else:
            print(f"Cost Change: {((optimized_cost - original_cost) / original_cost * 100):.2f}%")
        
        print("="*80 + "\n")


if __name__ == '__main__':
    unittest.main(verbosity=2)