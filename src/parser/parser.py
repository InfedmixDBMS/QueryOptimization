from ..tree.QueryTree import QueryTree
from ..tree.Nodes import NodeType, ConditionLeaf, ConditionOperator
from ..tree.ParsedQuery import ParsedQuery
from .lexer import tokenize, KEYWORDS
import re

def split_conditions(node: QueryTree):
    if node.type == NodeType.SELECT.value and isinstance(node.val, ConditionOperator):
        if node.val.operator == "AND":
            left = QueryTree(NodeType.SELECT.value, node.val.left, node.childs, node.parent)
            right = QueryTree(NodeType.SELECT.value, node.val.right, [left], node.parent)
            return right  
    return node

def parse_condition(condition_tokens, alias_map):
    if not condition_tokens:
        return None
    
    condition_str = " ".join(condition_tokens)
    for alias, table in alias_map.items():
        condition_str = re.sub(rf'\b{alias}\.', f"{table}.", condition_str)
    
    if "AND" in condition_tokens:
        and_idx = condition_tokens.index("AND")
        left_tokens = condition_tokens[:and_idx]
        right_tokens = condition_tokens[and_idx + 1:]
        
        left_condition = parse_condition(left_tokens, alias_map)
        right_condition = parse_condition(right_tokens, alias_map)
        
        if left_condition and right_condition:
            return ConditionOperator("AND", left_condition, right_condition)
    
    elif "OR" in condition_tokens:
        or_idx = condition_tokens.index("OR")
        left_tokens = condition_tokens[:or_idx]
        right_tokens = condition_tokens[or_idx + 1:]
        
        left_condition = parse_condition(left_tokens, alias_map)
        right_condition = parse_condition(right_tokens, alias_map)
        
        if left_condition and right_condition:
            return ConditionOperator("OR", left_condition, right_condition)
    
    else:
        cond = " ".join(condition_tokens)
        for alias, table in alias_map.items():
            cond = re.sub(rf'\b{alias}\.', f"{table}.", cond)
        return ConditionLeaf(cond)
    
    return ConditionLeaf(condition_str)

def parse_query(query: str) -> ParsedQuery:
    alias_map = {}
    tokens = tokenize(query)
    if "SELECT" not in tokens or "FROM" not in tokens:
        raise ValueError("Invalid query syntax")

    select_idx = tokens.index("SELECT")
    from_idx = tokens.index("FROM")
    where_idx = tokens.index("WHERE") if "WHERE" in tokens else len(tokens)

    # SELECT
    select_tokens = tokens[select_idx + 1: from_idx]
    raw_select_attrs = []
    current_attr = []
    for token in select_tokens:
        if token == ',':
            if current_attr:
                raw_select_attrs.append('.'.join(current_attr) if len(current_attr) > 1 else current_attr[0])
                current_attr = []
        else:
            current_attr.append(token)
    if current_attr:
        raw_select_attrs.append('.'.join(current_attr) if len(current_attr) > 1 else current_attr[0])
    
    select_attrs = []
    for attr in raw_select_attrs:
        for alias, table in alias_map.items():
            attr = re.sub(rf'^{alias}\.', f'{table}.', attr)
        select_attrs.append(attr)

    # FROM dengan JOINs
    from_tokens = tokens[from_idx + 1: where_idx]
    
    # CARI JOIN
    join_positions = []
    for i, token in enumerate(from_tokens):
        if token == "JOIN":
            join_positions.append(i)
    
    if not join_positions:
        # Simple FROM tanpa JOIN
        tables = []
        i = 0
        while i < len(from_tokens):
            if from_tokens[i] == ',':
                i += 1
                continue
            
            table_name = from_tokens[i]
            if (i + 1 < len(from_tokens) and 
                from_tokens[i + 1] != ',' and 
                from_tokens[i + 1].upper() not in KEYWORDS):
                alias = from_tokens[i + 1]
                tables.append((table_name, alias))
                i += 2
            else:
                tables.append((table_name, None))
                i += 1
        
        table_nodes = []
        for table_name, alias in tables:
            table_nodes.append(QueryTree(NodeType.TABLE.value, table_name, [], None))
            if alias:
                alias_map[alias] = table_name
        
    else:
        # Handle JOINs
        table_nodes = []
        
        # Parse tabel pertama
        first_table_tokens = from_tokens[:join_positions[0]]
        if len(first_table_tokens) >= 1:
            table_name = first_table_tokens[0]
            alias = first_table_tokens[1] if len(first_table_tokens) > 1 and first_table_tokens[1].upper() not in KEYWORDS else None
            first_table = QueryTree(NodeType.TABLE.value, table_name, [], None)
            
            # Bikin JOIN tree
            current_node = first_table
            for i, join_pos in enumerate(join_positions):
                if i + 1 < len(join_positions):
                    end_pos = join_positions[i + 1]
                else:
                    end_pos = len(from_tokens)
                
                join_tokens = from_tokens[join_pos:end_pos]
                
                # Parse JOIN: JOIN table alias ON condition
                if len(join_tokens) >= 2 and "ON" in join_tokens:
                    on_idx = join_tokens.index("ON")
                    
                    # Extract table info (antara JOIN and ON)
                    table_tokens = join_tokens[1:on_idx]
                    join_table_name = table_tokens[0]
                    join_alias = table_tokens[1] if len(table_tokens) > 1 and table_tokens[1].upper() not in KEYWORDS else None
                    
                    # Extract join condition (after ON)
                    condition_tokens = join_tokens[on_idx + 1:]
                    join_condition = parse_condition(condition_tokens, alias_map)
            
                    join_table = QueryTree(NodeType.TABLE.value, join_table_name, [], None)
                    join_node = QueryTree(NodeType.JOIN.value, join_condition, [], None)
                    join_node.add_child(current_node)
                    join_node.add_child(join_table)
                    
                    current_node = join_node
            
            table_nodes = [current_node]

    # PROJECT
    root = QueryTree(NodeType.PROJECT.value, select_attrs, [], None)

    # WHERE
    if where_idx < len(tokens):
        condition_tokens = tokens[where_idx + 1:]
        where_condition = parse_condition(condition_tokens, alias_map)
        where_node = QueryTree(NodeType.SELECT.value, where_condition, [], None)
        
        for tnode in table_nodes:
            where_node.add_child(tnode)
        root.add_child(where_node)
    else:
        # GAda WHERE
        for tnode in table_nodes:
            root.add_child(tnode)

    parsed = ParsedQuery(query, root)
    parsed.alias_map = alias_map
    return parsed