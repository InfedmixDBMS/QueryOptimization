from ..tree.QueryTree import QueryTree
from ..tree.Nodes import NodeType, ConditionLeaf
from ..tree.ParsedQuery import ParsedQuery
from .lexer import tokenize, KEYWORDS

def parse_query(query: str) -> ParsedQuery:
    tokens = tokenize(query)
    if "SELECT" not in tokens or "FROM" not in tokens:
        raise ValueError("Invalid query syntax")

    select_idx = tokens.index("SELECT")
    from_idx = tokens.index("FROM")
    where_idx = tokens.index("WHERE") if "WHERE" in tokens else len(tokens)

    # SELECT
    select_tokens = tokens[select_idx + 1: from_idx]
    select_attrs = []
    current_attr = []
    for token in select_tokens:
        if token == ',':
            if current_attr:
                select_attrs.append('.'.join(current_attr) if len(current_attr) > 1 else current_attr[0])
                current_attr = []
        else:
            current_attr.append(token)
    if current_attr:
        select_attrs.append('.'.join(current_attr) if len(current_attr) > 1 else current_attr[0])

    # FROM
    from_tokens = tokens[from_idx + 1: where_idx]
    tables = []
    i = 0
    while i < len(from_tokens):
        if from_tokens[i] == ',':
            i += 1
            continue
        
        table_name = from_tokens[i]
        # Cek untuk alias (koma atau keyword berikutnya)
        if (i + 1 < len(from_tokens) and 
            from_tokens[i + 1] != ',' and 
            from_tokens[i + 1].upper() not in KEYWORDS):
            alias = from_tokens[i + 1]
            tables.append((table_name, alias))
            i += 2
        else:
            tables.append((table_name, None))
            i += 1

    # Buat node
    table_nodes = []
    for table_info in tables:
        table_name, alias = table_info
        table_nodes.append(QueryTree(NodeType.TABLE.value, table_name, [], None))

    # root
    root = QueryTree(NodeType.PROJECT.value, select_attrs, [], None)

    # WHERE
    if where_idx < len(tokens):
        condition_tokens = tokens[where_idx + 1:]
        condition_str = " ".join(condition_tokens)
        condition_leaf = ConditionLeaf(condition_str)
        where_node = QueryTree(NodeType.SELECT.value, condition_leaf, [], None)
        
        for tnode in table_nodes:
            where_node.add_child(tnode)
        root.add_child(where_node)
    else:
        # Kalau gaada WHERE
        for tnode in table_nodes:
            root.add_child(tnode)

    parsed = ParsedQuery(query, root)
    return parsed