"""
Plan Optimizer Module - Applies optimization rules to query trees
"""

from .rules import OptimizationRules
from .cost_calculator import CostCalculator
from ..tree.parsed_query import ParsedQuery
import copy
import random
import time

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
        print("GENERATING MULTIPLE QUERY PLANS")
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
        tree = self.rules.push_down_selection(tree)
        tree = self.rules.push_down_projection(tree)
        tree = self.rules.combine_selections(tree)
        
        tree = self.rules.distribute_selection_over_join(tree)
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
        tree = self.rules.combine_cartesian_with_selection(tree)
        tree = self.rules.reorder_joins(tree)
        tree = self.rules.apply_associativity(tree)

        return tree

    def optimize_tree_with_genetic_algorithm(self, parsed_query, population_size=10, iterations=20, mutation_rate=0.3):
        """Optimize query tree using genetic algorithm"""
        original_tree = parsed_query.query_tree

        print("\n" + "="*60)
        print("GENETIC ALGORITHM OPTIMIZATION")
        print("="*60)
        print(f"Population Size: {population_size}")
        print(f"Generations: {iterations}")
        print(f"Mutation Rate: {mutation_rate}")
        print("-"*60)

        start_time = time.time()

        population = self._initialize_population(original_tree, population_size)

        best_scores = []
        avg_scores = []

        for gen in range(iterations):
            population.sort(key=lambda x: x[1])

            best_fitness = population[0][1]
            avg_fitness = sum(f for _, f in population) / len(population)

            best_scores.append(best_fitness)
            avg_scores.append(avg_fitness)

            print(f"Generation {gen+1:2d} | Best: {best_fitness:8.2f} | Avg: {avg_fitness:8.2f}")

            next_gen = [population[0]]

            while len(next_gen) < population_size:
                parent1 = self._selection(population)
                parent2 = self._selection(population)

                child1_rule_seq, child2_rule_seq = self._crossover(parent1[2], parent2[2])

                if random.random() < mutation_rate:
                    child1_rule_seq = self._mutate(child1_rule_seq)
                if random.random() < mutation_rate:
                    child2_rule_seq = self._mutate(child2_rule_seq)

                child1_tree = self._apply_rule_sequence(copy.deepcopy(original_tree), child1_rule_seq)
                child2_tree = self._apply_rule_sequence(copy.deepcopy(original_tree), child2_rule_seq)

                fitness1 = self.cost_calculator._calculate_tree_cost(child1_tree)
                fitness2 = self.cost_calculator._calculate_tree_cost(child2_tree)

                next_gen.append((child1_tree, fitness1, child1_rule_seq))
                if len(next_gen) < population_size:
                    next_gen.append((child2_tree, fitness2, child2_rule_seq))

            population = next_gen[:population_size]

        population.sort(key=lambda x: x[1])
        best_tree, best_fitness, best_sequence = population[0]

        duration = time.time() - start_time

        print("-"*60)
        print(f"Best Rule Sequence: {[self._rule_name(r) for r in best_sequence]}")
        print(f"Final Cost: {best_fitness:.2f}")
        print(f"Optimization Time: {duration:.3f}s")
        print("="*60 + "\n")

        return ParsedQuery(parsed_query.query, best_tree)

    def _initialize_population(self, original_tree, population_size):
        """Initialize population with random rule sequences"""
        population = []
        all_rules = list(range(8))

        for _ in range(population_size):
            rule_sequence = self._generate_random_rule_sequence(all_rules)
            tree = self._apply_rule_sequence(copy.deepcopy(original_tree), rule_sequence)
            fitness = self.cost_calculator._calculate_tree_cost(tree)
            population.append((tree, fitness, rule_sequence))

        return population

    def _generate_random_rule_sequence(self, all_rules):
        """Generate a random sequence of optimization rules"""
        sequence_length = random.randint(4, len(all_rules))
        rule_sequence = random.sample(all_rules, sequence_length)
        return rule_sequence

    def _apply_rule_sequence(self, tree, rule_sequence):
        """Apply a sequence of optimization rules to a tree"""
        for rule_id in rule_sequence:
            if rule_id == 0:
                tree = self.rules.push_down_selection(tree)
            elif rule_id == 1:
                tree = self.rules.swap_selection(tree)
            elif rule_id == 2:
                tree = self.rules.combine_selections(tree)
            elif rule_id == 3:
                tree = self.rules.push_down_projection(tree)
            elif rule_id == 4:
                tree = self.rules.distribute_selection_over_join(tree)
            elif rule_id == 5:
                tree = self.rules.combine_cartesian_with_selection(tree)
            elif rule_id == 6:
                tree = self.rules.reorder_joins(tree)
            elif rule_id == 7:
                tree = self.rules.apply_associativity(tree)

        return tree

    def _rule_name(self, rule_id):
        """Get readable name for rule ID"""
        rule_names = {
            0: "PushDownSel",
            1: "SwapSel",
            2: "CombineSel",
            3: "PushDownProj",
            4: "DistSelOverJoin",
            5: "CombineCartesian",
            6: "ReorderJoins",
            7: "Associativity"
        }
        return rule_names.get(rule_id, f"Rule{rule_id}")

    def _selection(self, population, tournament_size=3):
        """Tournament selection"""
        tournament_size = min(tournament_size, len(population))
        selected = random.sample(population, tournament_size)
        selected.sort(key=lambda x: x[1])
        return selected[0]

    def _crossover(self, seq1, seq2):
        """Single-point crossover for rule sequences"""
        if len(seq1) == 0 or len(seq2) == 0:
            return seq1.copy(), seq2.copy()

        min_len = min(len(seq1), len(seq2))
        if min_len <= 1:
            return seq1.copy(), seq2.copy()

        crossover_point = random.randint(1, min_len - 1)

        child1 = seq1[:crossover_point] + seq2[crossover_point:]
        child2 = seq2[:crossover_point] + seq1[crossover_point:]

        child1 = self._remove_duplicates_preserve_order(child1)
        child2 = self._remove_duplicates_preserve_order(child2)

        return child1, child2

    def _mutate(self, rule_sequence):
        """Mutate rule sequence by one of three operations:"""
        if len(rule_sequence) == 0:
            return [random.randint(0, 7)]

        mutation_type = random.randint(0, 2)
        new_sequence = rule_sequence.copy()

        if mutation_type == 0 and len(new_sequence) >= 2:
            idx1, idx2 = random.sample(range(len(new_sequence)), 2)
            new_sequence[idx1], new_sequence[idx2] = new_sequence[idx2], new_sequence[idx1]

        elif mutation_type == 1 and len(new_sequence) > 1:
            idx = random.randint(0, len(new_sequence) - 1)
            new_sequence.pop(idx)

        elif mutation_type == 2 and len(new_sequence) < 8:
            available_rules = [r for r in range(8) if r not in new_sequence]
            if available_rules:
                new_rule = random.choice(available_rules)
                insert_pos = random.randint(0, len(new_sequence))
                new_sequence.insert(insert_pos, new_rule)

        return new_sequence

    def _remove_duplicates_preserve_order(self, seq):
        """Remove duplicate rules while preserving order"""
        seen = set()
        result = []
        for item in seq:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result