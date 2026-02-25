#!/usr/bin/env python3
"""Generate PHP Repository pattern with PostgreSQL."""

import argparse

def generate_repository(entity_name, table_name, namespace=None):
    """Generate Repository pattern for PostgreSQL."""
    
    interface = f"""<?php
declare(strict_types=1);

{f'namespace {namespace};' if namespace else ''}

interface {entity_name}RepositoryInterface
{{
    public function find(int $id): ?{entity_name};
    public function findAll(): array;
    public function save({entity_name} $entity): void;
    public function delete(int $id): void;
}}
"""

    implementation = f"""<?php
declare(strict_types=1);

{f'namespace {namespace};' if namespace else ''}

use PDO;

final class {entity_name}Repository implements {entity_name}RepositoryInterface
{{
    public function __construct(
        private readonly PDO $connection
    ) {{
    }}

    public function find(int $id): ?{entity_name}
    {{
        $stmt = $this->connection->prepare(
            'SELECT * FROM {table_name} WHERE id = :id'
        );
        $stmt->execute(['id' => $id]);
        
        $data = $stmt->fetch(PDO::FETCH_ASSOC);
        
        return $data ? $this->hydrate($data) : null;
    }}

    public function findAll(): array
    {{
        $stmt = $this->connection->query(
            'SELECT * FROM {table_name} ORDER BY id'
        );
        
        $results = [];
        while ($data = $stmt->fetch(PDO::FETCH_ASSOC)) {{
            $results[] = $this->hydrate($data);
        }}
        
        return $results;
    }}

    public function save({entity_name} $entity): void
    {{
        if ($entity->getId() === null) {{
            $this->insert($entity);
        }} else {{
            $this->update($entity);
        }}
    }}

    public function delete(int $id): void
    {{
        $stmt = $this->connection->prepare(
            'DELETE FROM {table_name} WHERE id = :id'
        );
        $stmt->execute(['id' => $id]);
    }}

    private function insert({entity_name} $entity): void
    {{
        // Implement based on entity properties
        $stmt = $this->connection->prepare(
            'INSERT INTO {table_name} (/* columns */) 
             VALUES (/* :placeholders */) 
             RETURNING id'
        );
        
        // $stmt->execute([/* bindings */]);
        // $entity->setId((int)$this->connection->lastInsertId());
    }}

    private function update({entity_name} $entity): void
    {{
        // Implement based on entity properties
        $stmt = $this->connection->prepare(
            'UPDATE {table_name} 
             SET /* column = :placeholder */
             WHERE id = :id'
        );
        
        // $stmt->execute([/* bindings */]);
    }}

    private function hydrate(array $data): {entity_name}
    {{
        // Implement hydration based on entity constructor
        return new {entity_name}(/* ... */);
    }}
}}
"""

    return {"interface": interface, "implementation": implementation}

def main():
    parser = argparse.ArgumentParser(description="Generate Repository pattern")
    parser.add_argument("entity", help="Entity name")
    parser.add_argument("table", help="Database table name")
    parser.add_argument("-n", "--namespace", help="PHP namespace")
    parser.add_argument("-t", "--type", choices=["interface", "implementation", "both"], 
                       default="both", help="What to generate")
    
    args = parser.parse_args()
    
    result = generate_repository(args.entity, args.table, args.namespace)
    
    if args.type in ["interface", "both"]:
        print(result["interface"])
        if args.type == "both":
            print("\n" + "="*50 + "\n")
    
    if args.type in ["implementation", "both"]:
        print(result["implementation"])

if __name__ == "__main__":
    main()
