#!/usr/bin/env python3
"""Format SQL statements according to Riviere standard."""

import sys
import re
import argparse

def format_sql_riviere(sql):
    """Format SQL statement according to Riviere standard."""
    
    # Remove extra whitespace
    sql = " ".join(sql.split())
    
    # Keywords to uppercase
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
        'ON', 'AND', 'OR', 'IN', 'NOT', 'NULL', 'AS', 'ORDER', 'BY', 'GROUP',
        'HAVING', 'LIMIT', 'OFFSET', 'INSERT', 'INTO', 'VALUES', 'UPDATE',
        'SET', 'DELETE', 'CREATE', 'TABLE', 'INDEX', 'DROP', 'ALTER', 'ADD',
        'COLUMN', 'CONSTRAINT', 'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES',
        'CASCADE', 'RESTRICT', 'DEFAULT', 'UNIQUE', 'CHECK', 'EXISTS',
        'UNION', 'ALL', 'DISTINCT', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
        'WITH', 'RECURSIVE', 'RETURNING', 'USING', 'IS', 'BETWEEN', 'LIKE',
        'ILIKE', 'ANY', 'SOME', 'CAST', 'EXTRACT', 'DATE', 'TIME', 'TIMESTAMP'
    ]
    
    # Replace keywords
    for keyword in keywords:
        sql = re.sub(rf'\b{keyword}\b', keyword, sql, flags=re.IGNORECASE)
    
    # Format main clauses on new lines
    main_clauses = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
    
    formatted = []
    lines = sql.split('\n')
    
    for line in lines:
        # Main clauses on new line
        for clause in main_clauses:
            if clause in line:
                parts = line.split(clause)
                if len(parts) > 1:
                    before = parts[0].strip()
                    after = clause + ' ' + ' '.join(parts[1:]).strip()
                    if before:
                        formatted.append(before)
                    formatted.append(after)
                    line = ""
                    break
        
        if line:
            formatted.append(line)
    
    # Format JOINs
    result = []
    for line in formatted:
        if 'JOIN' in line and not line.strip().startswith('JOIN'):
            parts = re.split(r'((?:LEFT|RIGHT|INNER|OUTER)?\s*JOIN)', line)
            result.append(parts[0].strip())
            for i in range(1, len(parts), 2):
                if i < len(parts) - 1:
                    result.append(parts[i] + ' ' + parts[i+1].strip())
        else:
            result.append(line)
    
    # Add proper indentation
    indented = []
    indent_level = 0
    
    for line in result:
        line = line.strip()
        if not line:
            continue
            
        # Check for main clauses
        starts_with_main = any(line.startswith(clause) for clause in main_clauses)
        starts_with_join = 'JOIN' in line.split()[0] if line.split() else False
        
        if starts_with_main:
            indented.append(line)
            indent_level = 1
        elif starts_with_join:
            indented.append('  ' + line)
        elif line.startswith('AND') or line.startswith('OR'):
            indented.append('  ' * max(1, indent_level) + line)
        elif indent_level > 0:
            indented.append('  ' + line)
        else:
            indented.append(line)
    
    return '\n'.join(indented)

def main():
    parser = argparse.ArgumentParser(description="Format SQL according to Riviere standard")
    parser.add_argument("sql", nargs='?', help="SQL statement to format")
    parser.add_argument("-f", "--file", help="Read SQL from file")
    
    args = parser.parse_args()
    
    if args.file:
        with open(args.file, 'r') as f:
            sql = f.read()
    elif args.sql:
        sql = args.sql
    else:
        sql = sys.stdin.read()
    
    formatted = format_sql_riviere(sql)
    print(formatted)

if __name__ == "__main__":
    main()
