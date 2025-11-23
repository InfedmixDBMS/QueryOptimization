"""
Main Optimizer Module - Entry point for testing query optimization
"""

from .optimizer.optimization_engine import OptimizationEngine

def main():
    """
    Main function to demonstrate query parsing and optimization with multiple plans
    """
    optimizer = OptimizationEngine()

    # Example query
    query = """
        SELECT
            emp.employee_id,
            emp.name,
            dept.department_name,
            proj.project_name
        FROM
            employees emp
        INNER JOIN
            departments dept ON emp.department_id = dept.department_id
        INNER JOIN
            projects proj ON dept.department_id = proj.department_id
        WHERE
            emp.salary > 80000 
            AND emp.experience_years >= 5
            AND emp.age < 50
            AND dept.budget > 1000000
            AND proj.status = 'active'
    """

    print("="*60)
    print("QUERY OPTIMIZER - MULTIPLE PLAN SELECTION")
    print("="*60)
    
    # Parse query
    print("\nPARSING QUERY...")
    parsed_query = optimizer.parse_query(query)
    print(f"✓ Tables: {parsed_query.tables}")
    
    print("\nORIGINAL QUERY TREE:")
    parsed_query.print_tree()
    
    original_cost = optimizer.get_cost(parsed_query)
    print(f"\nOriginal Cost: {original_cost:.2f}")
    
    # Optimize with multiple plan selection
    print("\n" + "="*60)
    print("⚙️  OPTIMIZATION PHASE")
    print("="*60)
    
    optimized_query = optimizer.optimize_query(parsed_query)
    
    print("\nOPTIMIZED QUERY TREE:")
    optimized_query.print_tree()
    
    optimized_cost = optimizer.get_cost(optimized_query)
    print(f"\nOptimized Cost: {optimized_cost:.2f}")
    
    if original_cost > 0:
        improvement = original_cost - optimized_cost
        percentage = (improvement / original_cost) * 100
        print(f"\nIMPROVEMENT:")
        
        if improvement > 0:
            print(f"Cost Reduction: {improvement:.2f} units")
            print(f"Percentage: {percentage:.1f}%")
        elif improvement == 0:
            print(f"No change in cost")
        else:  # improvement < 0, cost naik
            cost_increase = abs(improvement)
            print(f"Cost Increase: {cost_increase:.2f} units")
            print(f"Percentage: {abs(percentage):.1f}%")
            print(f"Optimization increased cost (conservative plan used)")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()