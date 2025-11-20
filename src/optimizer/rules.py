"""
Optimization Rules Module - Implementation of query optimization rules

This module implements the equivalence rules from the specification:
1. Conjunctive selection decomposition
2. Selection commutativity
3. Projection cascade elimination
4. Selection with Cartesian product = join
5. Join commutativity
6. Join associativity
7. Selection distribution over join
8. Projection distribution over join
"""

from ..tree.nodes import ConditionNode, ConditionLeaf, ConditionOperator, NodeType
from ..tree.query_tree import QueryTree

class OptimizationRules:
    """
    Contains all optimization rules for query transformation
    """

    @staticmethod
    def push_down_selection(tree):
        """
        Breaks selection with AND conditions into chain of selection nodes
        """
        if tree is None:
            return None
        
        # Proses current node
        if tree.type == "SELECT" and isinstance(tree.val, ConditionNode):
            decomposed_tree = OptimizationRules._decompose_conjunctive_selection(tree)
            if decomposed_tree != tree:  # Kalau ada perubahan
                tree = decomposed_tree
        
        # Recursively apply to children
        if hasattr(tree, 'childs') and tree.childs:
            for i, child in enumerate(tree.childs):
                tree.childs[i] = OptimizationRules.push_down_selection(child)
        
        return tree

    @staticmethod
    def _decompose_conjunctive_selection(selection_node):
        """
        Helper function to decompose a selection node with AND conditions
        """
        
        condition = selection_node.val
        child = selection_node.childs[0] if selection_node.childs else None
        
        if child is None:
            return selection_node
        
        # Extract semua kondisi AND
        and_conditions = OptimizationRules._extract_and_conditions(condition)
        
        if len(and_conditions) <= 1:
            return selection_node
        
        current_tree = child
        
        for cond in reversed(and_conditions): 
            new_selection = QueryTree(NodeType.SELECT.value, cond, [], None)
            new_selection.add_child(current_tree)
            current_tree = new_selection
        
        return current_tree

    @staticmethod
    def _extract_and_conditions(condition_node):
        """
        Extract all individual conditions connected by AND operators
        """

        if isinstance(condition_node, ConditionLeaf):
            return [condition_node]
        
        elif isinstance(condition_node, ConditionOperator):
            if condition_node.operator == "AND":
                # Extract left adn rights
                left_conditions = OptimizationRules._extract_and_conditions(condition_node.left)
                right_conditions = OptimizationRules._extract_and_conditions(condition_node.right)
                return left_conditions + right_conditions
            else:
                # OR
                return [condition_node]
        
        else:
            # Unknown type
            return [condition_node]

    @staticmethod
    def push_down_projection(tree):
        """
        Push projection operations down the tree
        """
        # TODO: Implement push down projection
        return tree

    @staticmethod
    def combine_selections(tree):
        """
        Combine consecutive selection operations
        """
        if tree is None:
            return None
        
        # Cek kalau ada selection di atas selection
        if (tree.type == "SELECT" and 
            tree.childs and 
            tree.childs[0].type == "SELECT"):
            
            # Get parent and child conditions
            parent_condition = tree.val
            child_selection = tree.childs[0]
            child_condition = child_selection.val
            
            # Buat kondisi gabungan
            combined_condition = ConditionOperator("AND", parent_condition, child_condition)
            
            # Buat node selection gabungan
            combined_selection = QueryTree(NodeType.SELECT.value, combined_condition, [], None)
            
            # Tambah anak dari child selection
            if child_selection.childs:
                combined_selection.add_child(child_selection.childs[0])
            return combined_selection
        
        # Apply ke children recursively
        if hasattr(tree, 'childs') and tree.childs:
            for i, child in enumerate(tree.childs):
                tree.childs[i] = OptimizationRules.combine_selections(child)
        
        return tree

    @staticmethod
    def combine_cartesian_with_selection(tree):
        """
        Combine Cartesian product with selection to form join
        """
        # TODO: Implement cartesian-to-join transformation
        return tree

    @staticmethod
    def reorder_joins(tree):
        """
        Reorder joins based on commutativity
        """
        # TODO: Implement join reordering
        return tree

    @staticmethod
    def apply_associativity(tree):
        """
        Apply associativity rules to joins

        """
        # TODO: Implement join associativity
        return tree

    @staticmethod
    def distribute_selection_over_join(tree):
        """
        Distribute selection operations over join operations

        """
        # TODO: Implement selection distribution
        return tree

    @staticmethod
    def distribute_projection_over_join(tree):
        """
        Distribute projection operations over join operations

        """
        # TODO: Implement projection distribution
        return tree