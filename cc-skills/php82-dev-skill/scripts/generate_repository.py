#!/usr/bin/env python3
"""Generate PHP Repository pattern with PostgreSQL."""

import argparse


def namespace_line(namespace):
    """Return namespace declaration line, or empty string if none."""
    if namespace:
        return f"namespace {namespace};\n"
    return ""


def generate_repository(entity_name, table_name, namespace=None):
    """Generate Repository pattern for PostgreSQL."""

    ns = namespace_line(namespace)

    interface = f"""<?php
declare(strict_types=1);

{ns}
interface {entity_name}RepositoryInterface
{{
    public function find(int $id): ?{entity_name};

    /** @return list<{entity_name}> */
    public function findAll(): array;

    public function save({entity_name} $entity): void;

    public function delete(int $id): void;
}}
"""

    implementation = f"""<?php
declare(strict_types=1);

{ns}
use PDO;
use Psr\\Log\\LoggerInterface;

final class {entity_name}Repository implements {entity_name}RepositoryInterface
{{
    public function __construct(
        private readonly PDO $connection,
        private readonly LoggerInterface $logger,
    ) {{
    }}

    public function find(int $id): ?{entity_name}
    {{
        try {{
            $stmt = $this->connection->prepare(
                'SELECT * FROM {table_name} WHERE id = :id'
            );
            $stmt->execute(['id' => $id]);

            $data = $stmt->fetch(PDO::FETCH_ASSOC);

            return $data !== false ? $this->hydrate($data) : null;
        }} catch (\\PDOException $e) {{
            $this->logger->error('Failed to find {entity_name}', [
                'id'        => $id,
                'exception' => $e->getMessage(),
            ]);
            throw $e;
        }}
    }}

    /** @return list<{entity_name}> */
    public function findAll(): array
    {{
        try {{
            $stmt = $this->connection->query(
                'SELECT * FROM {table_name} ORDER BY id'
            );

            $results = [];
            while ($data = $stmt->fetch(PDO::FETCH_ASSOC)) {{
                $results[] = $this->hydrate($data);
            }}

            return $results;
        }} catch (\\PDOException $e) {{
            $this->logger->error('Failed to fetch all {entity_name} records', [
                'exception' => $e->getMessage(),
            ]);
            throw $e;
        }}
    }}

    public function save({entity_name} $entity): void
    {{
        try {{
            if ($entity->getId() === null) {{
                $this->insert($entity);
            }} else {{
                $this->update($entity);
            }}
        }} catch (\\PDOException $e) {{
            $this->logger->error('Failed to save {entity_name}', [
                'exception' => $e->getMessage(),
            ]);
            throw $e;
        }}
    }}

    public function delete(int $id): void
    {{
        try {{
            $stmt = $this->connection->prepare(
                'DELETE FROM {table_name} WHERE id = :id'
            );
            $stmt->execute(['id' => $id]);
        }} catch (\\PDOException $e) {{
            $this->logger->error('Failed to delete {entity_name}', [
                'id'        => $id,
                'exception' => $e->getMessage(),
            ]);
            throw $e;
        }}
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
        // $entity->setId((int) $stmt->fetchColumn());
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

    /**
     * @param array<string, mixed> $data
     */
    private function hydrate(array $data): {entity_name}
    {{
        // TODO: replace with actual constructor arguments matching {entity_name}
        return new {entity_name}(...$data);
    }}
}}
"""

    return {{"interface": interface, "implementation": implementation}}


def main():
    parser = argparse.ArgumentParser(description="Generate Repository pattern")
    parser.add_argument("entity", help="Entity name")
    parser.add_argument("table", help="Database table name")
    parser.add_argument("-n", "--namespace", help="PHP namespace")
    parser.add_argument(
        "-t",
        "--type",
        choices=["interface", "implementation", "both"],
        default="both",
        help="What to generate",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    result = generate_repository(args.entity, args.table, args.namespace)

    output_parts = []

    if args.type in ["interface", "both"]:
        output_parts.append(result["interface"])
        if args.type == "both":
            output_parts.append("\n" + "=" * 50 + "\n")

    if args.type in ["implementation", "both"]:
        output_parts.append(result["implementation"])

    output = "\n".join(output_parts)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
