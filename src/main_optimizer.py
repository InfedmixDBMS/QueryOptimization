"""
Main Optimizer Module - Entry point for testing query optimization
"""

from .optimizer.optimization_engine import OptimizationEngine


def main():
    """
    Main function to demonstrate query parsing and optimization
    """
    optimizer = OptimizationEngine()

    # Example complex query with multiple joins and conditions
    query = """
        SELECT
            emp.employee_id,
            emp.name AS employee_name,
            dept.department_name,
            proj.project_name,
            proj.budget
        FROM
            employees emp
        INNER JOIN
            departments dept ON emp.department_id = dept.department_id
        INNER JOIN
            projects proj ON dept.department_id = proj.department_id
        WHERE
            (emp.salary > 80000 AND emp.experience_years >= 5)
            OR proj.budget > 1000000
        ORDER BY
            emp.salary DESC,
            proj.budget DESC
    """

    print("=== PARSING ===")
    parsed_query = optimizer.parse_query(query)
    print(f"Tables: {parsed_query.tables}")
    print("Original Tree:")
    parsed_query.print_tree()
    
    print(f"\nOriginal Cost: {optimizer.get_cost(parsed_query)}")

    print("\n=== OPTIMIZATION ===")
    optimized_query = optimizer.optimize_query(parsed_query)
    print("Optimized Tree:")
    optimized_query.print_tree()
    
    print(f"\nOptimized Cost: {optimizer.get_cost(optimized_query)}")


if __name__ == "__main__":
    main()