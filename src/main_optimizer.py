from .optimizer.OptimizationEngine import OptimizationEngine

def main():
    optimizer = OptimizationEngine()
    parsed_query = optimizer.parse_query("""
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
""")
    print("Parsed Query:")
    print(f"Original query: {parsed_query.query}")
    print(f"Tables: {parsed_query.tables}")
    print("Query Tree:")
    parsed_query.print_tree()

if __name__ == "__main__":
    main()