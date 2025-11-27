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
        
        # Rekursif bottom up
        if hasattr(tree, 'childs') and tree.childs:
            for i, child in enumerate(tree.childs):
                tree.childs[i] = OptimizationRules.push_down_selection(child)
        
        # Process current node
        if tree.type == "SELECT":
            original = tree
            tree = OptimizationRules._decompose_conjunctive_selection(tree)

            if tree != original:
                tree = OptimizationRules.push_down_selection(tree) 

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
            new_tree = OptimizationRules._helper_distribute_projection_over_join(tree)
            return new_tree  # STOP here, don't recurse

        # Only recurse if NOT PROJECT
        for child in tree.childs:
            tree.childs[i] = OptimizationRules.push_down_projection(child)
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
    def swap_selection(tree):
        """
        Rule 2: Selection Commutativity
        """
        if tree is None:
            return None
        
        # SELECT node with a SELECT child
        if (tree.type != "SELECT" or 
            not tree.childs or 
            tree.childs[0].type != "SELECT"):
            if hasattr(tree, 'childs') and tree.childs:
                for i, child in enumerate(tree.childs):
                    tree.childs[i] = OptimizationRules.swap_selection(child)
            return tree
        
        parent_condition = tree.val
        child_selection = tree.childs[0]
        child_condition = child_selection.val
        grandchild = child_selection.childs[0] if child_selection.childs else None
        
        if grandchild is None:
            return tree
        
        # swapped conditions
        new_parent = QueryTree(NodeType.SELECT.value, child_condition, [], None)
        new_child = QueryTree(NodeType.SELECT.value, parent_condition, [], None)
        
        # new_parent -> new_child -> grandchild
        new_child.add_child(grandchild)
        new_parent.add_child(new_child)
        
        # recursive
        if hasattr(new_parent, 'childs') and new_parent.childs:
            for i, child in enumerate(new_parent.childs):
                new_parent.childs[i] = OptimizationRules.swap_selection(child)
        
        return new_parent

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
        if tree is None:
            return None
            
        # recursive
        if hasattr(tree, 'childs') and tree.childs:
            for i, child in enumerate(tree.childs):
                tree.childs[i] = OptimizationRules.distribute_selection_over_join(child)
                
        if tree.type != "SELECT" or not tree.childs:
            return tree
            
        child = tree.childs[0]
        
        if child.type not in ["JOIN", "NATURAL-JOIN"]:
            return tree
            
        condition = tree.val
        left_subtree = child.childs[0] if len(child.childs) > 0 else None
        right_subtree = child.childs[1] if len(child.childs) > 1 else None
        
        if not left_subtree or not right_subtree:
            return tree
        
        left_attrs = OptimizationRules._get_attributes_from_tree(left_subtree)
        right_attrs = OptimizationRules._get_attributes_from_tree(right_subtree)
        and_conditions = OptimizationRules._extract_and_conditions(condition)
        
        left_conditions = []
        right_conditions = []
        both_conditions = []
        
        for cond in and_conditions:
            cond_attrs = OptimizationRules._get_attributes_from_condition(cond)
            
            if not cond_attrs:
                both_conditions.append(cond)
                continue
            is_left = all(OptimizationRules._attribute_belongs_to(attr, left_attrs) for attr in cond_attrs)
            is_right = all(OptimizationRules._attribute_belongs_to(attr, right_attrs) for attr in cond_attrs)
            
            if is_left and not is_right:
                left_conditions.append(cond)
            elif is_right and not is_left:
                right_conditions.append(cond)
            else:
                both_conditions.append(cond)
        
        new_left = left_subtree
        new_right = right_subtree
        if left_conditions:
            combined_left = left_conditions[0]
            for cond in left_conditions[1:]:
                combined_left = ConditionOperator("AND", combined_left, cond)
            
            new_left = QueryTree(NodeType.SELECT.value, combined_left, [], None)
            new_left.add_child(left_subtree)
        if right_conditions:
            combined_right = right_conditions[0]
            for cond in right_conditions[1:]:
                combined_right = ConditionOperator("AND", combined_right, cond)
            
            new_right = QueryTree(NodeType.SELECT.value, combined_right, [], None)
            new_right.add_child(right_subtree)
        
        new_join = QueryTree(child.type, child.val, [], None)
        new_join.add_child(new_left)
        new_join.add_child(new_right)
        
        if both_conditions:
            combined_both = both_conditions[0]
            for cond in both_conditions[1:]:
                combined_both = ConditionOperator("AND", combined_both, cond)
            
            final_select = QueryTree(NodeType.SELECT.value, combined_both, [], None)
            final_select.add_child(new_join)
            return final_select
        
        return new_join
        
    def distribute_projection_over_join(tree):
        """
        Distribute projection operations over join operations

        """

        return OptimizationRules._helper_distribute_projection_over_join(tree)

### HELPER ###
    @staticmethod
    def _helper_distribute_projection_over_join(tree):
        """
        Rule 8: Distribute projection over join helper
        """
        if tree.type != "PROJECT" or not tree.childs:
            return tree
        
        child = tree.childs[0]

        # Skip select to find join
        join_node = child
        intermediate_nodes = [] 
        
        while join_node and join_node.type == "SELECT":
            intermediate_nodes.append(join_node)
            join_node = join_node.childs[0] if join_node.childs else None
        
        # cek join
        if not join_node or join_node.type not in ["JOIN", "NATURAL-JOIN"]:
            return tree
        
        if len(join_node.childs) < 2:
            return tree
        
        project_attrs = tree.val
        if isinstance(project_attrs, str):
            project_attrs = [attr.strip() for attr in project_attrs.split(',')]
        elif not isinstance(project_attrs, list):
            project_attrs = [str(project_attrs)]
        
        join_condition = join_node.val
        left_subtree = join_node.childs[0]
        right_subtree = join_node.childs[1]
        
        # Get attrs dari each side
        left_attrs = OptimizationRules._get_attributes_from_tree(left_subtree)
        right_attrs = OptimizationRules._get_attributes_from_tree(right_subtree)
        
        # Get join attrs
        join_attrs = OptimizationRules._get_attributes_from_condition(join_condition)
        
        # Split project attributes
        L1 = []  # Attributes from left
        L2 = []  # Attributes from right
        
        for attr in project_attrs:
            if OptimizationRules._attribute_belongs_to(attr, left_attrs):
                L1.append(attr)
            elif OptimizationRules._attribute_belongs_to(attr, right_attrs):
                L2.append(attr)
            else:
                L1.append(attr)  # Default to left
                print(f"[Warning] Ambiguous attribute '{attr}' assigned to left side")
        
        # L3: join attributes kiri yang gaada di L1
        L3 = [attr for attr in join_attrs 
            if attr not in L1 and OptimizationRules._attribute_belongs_to(attr, left_attrs)]
        
        # L4: join attributes kanan yang gaada di in L2
        L4 = [attr for attr in join_attrs 
            if attr not in L2 and OptimizationRules._attribute_belongs_to(attr, right_attrs)]
        
        # craete new
        left_project_attrs = list(set(L1 + L3)) if (L1 or L3) else None
        right_project_attrs = list(set(L2 + L4)) if (L2 or L4) else None
        
        # buidl new
        new_left = left_subtree
        if left_project_attrs:
            # string consistency
            left_proj_str = ', '.join(left_project_attrs)
            left_proj = QueryTree(NodeType.PROJECT.value, left_proj_str, [], None)
            left_proj.add_child(left_subtree)
            new_left = left_proj
        
        new_right = right_subtree
        if right_project_attrs:
            right_proj_str = ', '.join(right_project_attrs)
            right_proj = QueryTree(NodeType.PROJECT.value, right_proj_str, [], None)
            right_proj.add_child(right_subtree)
            new_right = right_proj
        
        # rebuild join
        new_join = QueryTree(join_node.type, join_node.val, [], None)
        new_join.add_child(new_left)
        new_join.add_child(new_right)

        current = new_join
        for select_node in reversed(intermediate_nodes):
            new_select = QueryTree(select_node.type, select_node.val, [], None)
            new_select.add_child(current)
            current = new_select
        
        # Outer projection if join attributes were added
        if L3 or L4:
            # convert string
            outer_proj_str = ', '.join(project_attrs)
            outer_proj = QueryTree(NodeType.PROJECT.value, outer_proj_str, [], None)
            outer_proj.add_child(current)
            return outer_proj
        
        return current

    @staticmethod
    def _attribute_belongs_to(attr, table_attrs):
        """Helper: Check if attribute belongs to a table"""
        if '.' not in attr:
            return False
        
        attr_prefix = attr.split('.')[0].lower()  # 'emp', 'dept'
        
        for table_attr in table_attrs:
            if table_attr.endswith('.*'):
                # Extract table name: "employees.*" → "employees"
                table_name = table_attr.replace('.*', '').lower()
                
                # Match: emp → employees, dept → departments
                # Check if prefix is substring of table name OR vice versa
                if attr_prefix in table_name or table_name.startswith(attr_prefix):
                    return True
            
            # Exact match: emp.id == emp.id
            if table_attr.lower().startswith(f"{attr_prefix}."):
                return True
        
        return False

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
            table_name = tree.val  # e.g., "employees"
            
            # Add full table name
            attrs.append(table_name + ".*")  # "employees.*"
            
            # ✅ ADD ALIAS if exists
            if hasattr(tree, 'alias') and tree.alias:
                attrs.append(tree.alias + ".*")  # "emp.*"
        
        elif tree.type == "PROJECT":
            proj_attrs = tree.val
            if isinstance(proj_attrs, str):
                attrs.extend([attr.strip() for attr in proj_attrs.split(',')])
            elif isinstance(proj_attrs, list):
                attrs.extend(proj_attrs)
            else:
                attrs.append(str(proj_attrs))
        
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
            identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*', cond_str)
            attrs.extend(identifiers)
        
        elif isinstance(condition, ConditionOperator):
            attrs.extend(OptimizationRules._get_attributes_from_condition(condition.left))
            attrs.extend(OptimizationRules._get_attributes_from_condition(condition.right))
        
        return list(set(attrs))  # removee duplicates