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

### MAIN ###
    @staticmethod
    def push_down_selection(tree):
        """
        Breaks selection with AND conditions into chain of selection nodes
        and distributes them over joins
        """
        if tree is None:
            return None
        
        # Apply recursively to children first (bottom-up)
        if hasattr(tree, 'childs') and tree.childs:
            for i, child in enumerate(tree.childs):
                tree.childs[i] = OptimizationRules.push_down_selection(child)
        
        # Process current node
        if tree.type == "SELECT":
            tree = OptimizationRules._decompose_conjunctive_selection(tree)
            
            # tree = OptimizationRules._push_selection_over_join(tree) -> Ini buat integrate sama rules 7 ya
        
        return tree

    @staticmethod
    def push_down_projection(tree):
        """
        Push projection operations down the tree -> Ini masih buat rule 8 dulu, kalau ada yg make rules lain bisa ditambahin disini
        """
        if tree is None:
            return None
        
        # Apply recursively to children first (bottom-up)
        if hasattr(tree, 'childs') and tree.childs:
            for i, child in enumerate(tree.childs):
                tree.childs[i] = OptimizationRules.push_down_projection(child)
        
        # Process current node
        if tree.type == "PROJECT":
            # Eliminate cascade projections (Rule 3)
            # tree = OptimizationRules._eliminate_projection_cascade(tree) -> Rule 3 taro sini sih harusnya
            
            # Try to distribute over join (Rule 8)
            tree = OptimizationRules._helper_distribute_projection_over_join(tree)
        
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

        return OptimizationRules._helper_distribute_projection_over_join(tree)

### HELPER ###
    @staticmethod
    def _helper_distribute_projection_over_join(tree):
        """
        Rule 8: Distribute projection over join
        """
        if tree.type != "PROJECT" or not tree.childs:
            return tree
        
        child = tree.childs[0]
        
        if child.type not in ["JOIN", "NATURAL-JOIN"]:
            return tree
        
        if len(child.childs) < 2:
            return tree
        
        project_attrs = tree.val 
        join_condition = child.val
        left_subtree = child.childs[0]
        right_subtree = child.childs[1]
        
        # Get attributes left and rigth
        left_attrs = OptimizationRules._get_attributes_from_tree(left_subtree)
        right_attrs = OptimizationRules._get_attributes_from_tree(right_subtree)
        
        # Get join attributes
        join_attrs = OptimizationRules._get_attributes_from_condition(join_condition)
        
        # Split project attributes
        L1 = []  # Attributes left
        L2 = []  # Attributes right
        
        for attr in project_attrs:
            # Handle "table.attr" atau "attr"
            attr_name = attr.split('.')[-1] if '.' in attr else attr
            attr_name = attr_name.split()[0]  # Remove AS 
            
            # Check if attribute left/right
            if any(attr_name.lower() in la.lower() for la in left_attrs) or \
               any(attr.lower() in la.lower() for la in left_attrs):
                L1.append(attr)
            elif any(attr_name.lower() in ra.lower() for ra in right_attrs) or \
                 any(attr.lower() in ra.lower() for ra in right_attrs):
                L2.append(attr)
            else:
                # Untuk yg ambigu
                L1.append(attr)
                L2.append(attr)
        
        # L3: join attributes from left not in project list
        L3 = []
        for attr in join_attrs:
            if attr not in L1 and any(attr.lower() in la.lower() for la in left_attrs):
                L3.append(attr)
        
        # L4: join attributes from right not in project list
        L4 = []
        for attr in join_attrs:
            if attr not in L2 and any(attr.lower() in ra.lower() for ra in right_attrs):
                L4.append(attr)
        
        # new projection
        left_project_attrs = list(set(L1 + L3)) if (L1 or L3) else ['*']
        right_project_attrs = list(set(L2 + L4)) if (L2 or L4) else ['*']
        
        # create new nodes
        new_left = left_subtree
        if left_project_attrs != ['*'] and len(left_project_attrs) > 0:
            left_proj = QueryTree(NodeType.PROJECT.value, left_project_attrs, [], None)
            left_proj.add_child(left_subtree)
            new_left = left_proj
        
        new_right = right_subtree
        if right_project_attrs != ['*'] and len(right_project_attrs) > 0:
            right_proj = QueryTree(NodeType.PROJECT.value, right_project_attrs, [], None)
            right_proj.add_child(right_subtree)
            new_right = right_proj
        
        # rebuild 
        new_join = QueryTree(child.type, child.val, [], None)
        new_join.add_child(new_left)
        new_join.add_child(new_right)
        
        # outer projection (klo butuh)
        if L3 or L4:
            outer_proj = QueryTree(NodeType.PROJECT.value, project_attrs, [], None)
            outer_proj.add_child(new_join)
            return outer_proj
        
        return new_join

    @staticmethod
    def _decompose_conjunctive_selection(selection_node):
        """
        Helper: function to decompose a selection node with AND conditions
        """
        condition = selection_node.val
        child = selection_node.childs[0] if selection_node.childs else None
        
        if child is None:
            return selection_node
        
        # extract AND
        and_conditions = OptimizationRules._extract_and_conditions(condition)
        
        if len(and_conditions) <= 1:
            return selection_node
        
        # build chain
        current_tree = child
        
        for cond in reversed(and_conditions): 
            new_selection = QueryTree(NodeType.SELECT.value, cond, [], None)
            new_selection.add_child(current_tree)
            current_tree = new_selection
        
        return current_tree

    @staticmethod
    def _extract_and_conditions(condition_node):
        """
        Helper: Extract all individual conditions connected by AND operators
        """
        if isinstance(condition_node, ConditionLeaf):
            return [condition_node]
        
        elif isinstance(condition_node, ConditionOperator):
            if condition_node.operator == "AND":
                left_conditions = OptimizationRules._extract_and_conditions(condition_node.left)
                right_conditions = OptimizationRules._extract_and_conditions(condition_node.right)
                return left_conditions + right_conditions
            else:
                # OR or otehr operators 
                return [condition_node]
        
        else:
            return [condition_node]
        
    @staticmethod
    def _get_attributes_from_tree(tree):
        """Get all attributes available from a subtree"""
        attrs = []
        
        if tree.type == "TABLE":
            # return table name
            attrs.append(tree.val + ".*")
        elif tree.type == "PROJECT":
            attrs.extend(tree.val if isinstance(tree.val, list) else [tree.val])
        
        # Recursively collect from children
        for child in tree.childs:
            attrs.extend(OptimizationRules._get_attributes_from_tree(child))
        
        return attrs

    @staticmethod
    def _get_attributes_from_condition(condition):
        """Extract attribute names from a condition"""
        attrs = []
        
        if condition is None:
            return attrs
        
        if isinstance(condition, ConditionLeaf):
            # Parse kondisi "emp.id = dept.id"
            cond_str = condition.condition
            # Extract identifiers (words before/after operators)
            import re
            identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_.]*', cond_str)
            attrs.extend(identifiers)
        
        elif isinstance(condition, ConditionOperator):
            attrs.extend(OptimizationRules._get_attributes_from_condition(condition.left))
            attrs.extend(OptimizationRules._get_attributes_from_condition(condition.right))
        
        return list(set(attrs))  # removee duplicates