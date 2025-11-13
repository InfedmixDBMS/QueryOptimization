import re

KEYWORDS = {"SELECT", "FROM", "WHERE", "JOIN", "ON", "AND", "OR", "ORDER", "BY", "INNER", "LEFT", "RIGHT", "OUTER", "AS", "GROUP", "HAVING"}

def tokenize(query: str):
    query = query.strip()
    tokens = re.findall(r"'[^']*'|\"[^\"]*\"|[A-Za-z_][A-Za-z0-9_.]*|<=|>=|<>|!=|=|<|>|\*|,|\(|\)|\d+", query)
    return [t.upper() if t.upper() in KEYWORDS else t for t in tokens]