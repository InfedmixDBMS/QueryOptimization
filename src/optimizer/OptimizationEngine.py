from parser import parse_query
# from plan_optimizer import optimize_tree
# from cost_estimator import estimate_cost

class OptimizationEngine:
    def parse_query(self, query: str):
        return parse_query(query)

    # def optimize_query(self, parsed_query):
    #     pass

    # def get_cost(self, parsed_query):
    #     pass