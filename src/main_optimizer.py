from .parser.parser import parse_query
# from .optimizer.plan_optimizer import optimize_tree
# from .optimizer.cost_estimator import estimate_cost

class QueryOptimizer:
    def parse_query(self, query: str):
        return parse_query(query)

    # def optimize_query(self, parsed_query):
    #     pass

    # def get_cost(self, parsed_query):
    #     pass

def main():
    optimizer = QueryOptimizer()
    parsed_query = optimizer.parse_query("SELECT s.name, d.nama FROM student s JOIN dept d ON s.dept_id = d.id JOIN apt a ON a.id = s.dept_id WHERE s.age > 20 AND d.size >= 10 AND a.name = 'bebek'")
    print("Parsed Query:")
    print(f"Original query: {parsed_query.query}")
    print(f"Tables: {parsed_query.tables}")
    print("Query Tree:")
    parsed_query.print_tree()

if __name__ == "__main__":
    main()