from ..tree.nodes import ConditionNode, ConditionLeaf, ConditionOperator
import math


class Statistics:
    def __init__(self):
        self.relations = {}

    def add_relation(self, relation_name, nr, lr, br=None, fr=None):
        if br is None and fr is not None:
            br = math.ceil(nr / fr)
        elif br is None and fr is None:
            fr = 100
            br = math.ceil(nr / fr)
        elif fr is None:
            fr = math.ceil(nr / br) if br > 0 else 1

        self.relations[relation_name] = {
            'nr': nr,
            'lr': lr,
            'br': br,
            'fr': fr,
            'distinct_values': {}
        }

    def add_distinct_values(self, relation_name, attribute, count):
        if relation_name in self.relations:
            self.relations[relation_name]['distinct_values'][attribute] = count

    def get_relation_stats(self, relation_name):
        return self.relations.get(relation_name, {
            'nr': 1000,
            'lr': 100,
            'br': 10,
            'fr': 100,
            'distinct_values': {}
        })

    def get_distinct_values(self, relation_name, attribute):
        stats = self.get_relation_stats(relation_name)
        return stats['distinct_values'].get(attribute, stats['nr'] // 10)


class CostCalculator:
    def __init__(self, statistics=None):
        self.statistics = statistics if statistics else Statistics()
        self._init_default_statistics()

    def _init_default_statistics(self):
        default_relations = ['employees', 'departments', 'projects', 'emp', 'dept', 'proj']
        for rel in default_relations:
            if rel not in self.statistics.relations:
                self.statistics.add_relation(rel, 1000, 100, 10, 100)

    def get_cost(self, parsed_query):
        return self._calculate_tree_cost(parsed_query.query_tree)

    def _calculate_tree_cost(self, tree):
        if tree is None:
            return 0

        node_type = tree.type.upper()

        if node_type == "TABLE":
            return self._calculate_table_cost(tree)
        elif node_type == "SELECT":
            return self._calculate_select_cost(tree)
        elif node_type == "PROJECT":
            return self._calculate_project_cost(tree)
        elif node_type == "JOIN":
            return self._calculate_join_cost(tree)
        elif node_type == "NATURAL-JOIN":
            return self._calculate_natural_join_cost(tree)
        elif node_type == "HASH-JOIN":
            return self._calculate_hash_join_cost(tree)
        elif node_type == "CARTESIAN-PRODUCT":
            return self._calculate_cartesian_product_cost(tree)
        elif node_type == "ORDER-BY":
            return self._calculate_order_by_cost(tree)
        elif node_type == "UPDATE":
            return self._calculate_update_cost(tree)
        elif node_type == "LIMIT":
            return self._calculate_limit_cost(tree)
        else:
            child_costs = sum(self._calculate_tree_cost(child) for child in tree.childs)
            return child_costs

    def _calculate_table_cost(self, tree):
        table_name = tree.val
        stats = self.statistics.get_relation_stats(table_name)
        return stats['br']

    def _calculate_select_cost(self, tree):
        if not tree.childs:
            return 0

        child_cost = self._calculate_tree_cost(tree.childs[0])
        condition = tree.val
        selectivity = self._estimate_selectivity(condition, tree)

        output_cost = child_cost * selectivity
        print(f"    [SELECT DEBUG] Child cost: {child_cost:.2f}, Selectivity: {selectivity:.4f}, Output: {output_cost:.2f}")

        return output_cost

    def _calculate_project_cost(self, tree):
        if not tree.childs:
            return 0

        child_cost = self._calculate_tree_cost(tree.childs[0])
        projection_overhead = child_cost * 0.1
        print(f"    [PROJECT DEBUG] Child cost: {child_cost:.2f}, Overhead: {projection_overhead:.2f}, Total: {child_cost + projection_overhead:.2f}")

        return child_cost + projection_overhead

    def _calculate_join_cost(self, tree):
        if len(tree.childs) < 2:
            return sum(self._calculate_tree_cost(child) for child in tree.childs)

        left_cost = self._calculate_tree_cost(tree.childs[0])
        right_cost = self._calculate_tree_cost(tree.childs[1])
        
        # DEBUGGING
        print(f"    [JOIN DEBUG] Left cost: {left_cost:.2f}, Right cost: {right_cost:.2f}")

        nested_loop_cost = left_cost * right_cost
        join_overhead = (left_cost + right_cost) * 0.5
        
        total = nested_loop_cost + join_overhead
        print(f"    [JOIN DEBUG] Nested loop: {nested_loop_cost:.2f}, Total: {total:.2f}")

        return total

    def _calculate_natural_join_cost(self, tree):
        if len(tree.childs) < 2:
            return sum(self._calculate_tree_cost(child) for child in tree.childs)

        left_cost = self._calculate_tree_cost(tree.childs[0])
        right_cost = self._calculate_tree_cost(tree.childs[1])

        merge_join_cost = left_cost + right_cost
        join_overhead = (left_cost + right_cost) * 0.3

        return merge_join_cost + join_overhead

    def _calculate_hash_join_cost(self, tree):
        if len(tree.childs) < 2:
            return sum(self._calculate_tree_cost(child) for child in tree.childs)

        left_cost = self._calculate_tree_cost(tree.childs[0])
        right_cost = self._calculate_tree_cost(tree.childs[1])

        hash_build_cost = left_cost
        hash_probe_cost = right_cost
        hash_overhead = (left_cost + right_cost) * 0.2

        return hash_build_cost + hash_probe_cost + hash_overhead

    def _calculate_cartesian_product_cost(self, tree):
        if len(tree.childs) < 2:
            return sum(self._calculate_tree_cost(child) for child in tree.childs)

        left_cost = self._calculate_tree_cost(tree.childs[0])
        right_cost = self._calculate_tree_cost(tree.childs[1])

        cartesian_cost = left_cost * right_cost

        return cartesian_cost

    def _calculate_order_by_cost(self, tree):
        if not tree.childs:
            return 0

        child_cost = self._calculate_tree_cost(tree.childs[0])

        estimated_tuples = child_cost * 100
        sort_cost = estimated_tuples * math.log2(max(estimated_tuples, 1))

        return child_cost + sort_cost

    def _calculate_update_cost(self, tree):
        if not tree.childs:
            return 0

        child_cost = self._calculate_tree_cost(tree.childs[0])
        update_overhead = child_cost * 1.5

        return child_cost + update_overhead

    def _calculate_limit_cost(self, tree):
        if not tree.childs:
            return 0

        child_cost = self._calculate_tree_cost(tree.childs[0])

        limit_value = tree.val if isinstance(tree.val, (int, float)) else 100
        reduction_factor = min(limit_value / 1000, 1.0)

        return child_cost * reduction_factor

    def _estimate_selectivity(self, condition, tree):
        if condition is None:
            return 1.0

        if isinstance(condition, ConditionNode):
            return self._estimate_condition_selectivity(condition, tree)

        if isinstance(condition, str):
            if '=' in condition:
                return 0.1
            elif '>' in condition or '<' in condition:
                return 0.3
            elif 'LIKE' in condition.upper():
                return 0.2
            else:
                return 0.5

        return 0.5

    def _estimate_condition_selectivity(self, condition_node, tree):
        if isinstance(condition_node, ConditionLeaf):
            condition_str = condition_node.condition

            if '=' in condition_str:
                return 0.1
            elif '>=' in condition_str or '<=' in condition_str:
                return 0.4
            elif '>' in condition_str or '<' in condition_str:
                return 0.3
            elif '<>' in condition_str or '!=' in condition_str:
                return 0.9
            else:
                return 0.5

        elif isinstance(condition_node, ConditionOperator):
            left_selectivity = self._estimate_condition_selectivity(condition_node.left, tree)
            right_selectivity = self._estimate_condition_selectivity(condition_node.right, tree)

            if condition_node.operator.upper() == 'AND':
                return left_selectivity * right_selectivity
            elif condition_node.operator.upper() == 'OR':
                return left_selectivity + right_selectivity - (left_selectivity * right_selectivity)
            else:
                return (left_selectivity + right_selectivity) / 2

        return 0.5

    def calculate_node_cost(self, node):
        return self._calculate_tree_cost(node)


def get_cost(parsed_query):
    calculator = CostCalculator()
    return calculator.get_cost(parsed_query)