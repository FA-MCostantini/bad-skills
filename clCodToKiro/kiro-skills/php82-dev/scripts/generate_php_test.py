#!/usr/bin/env python3
"""Generate PHP test file (PHPUnit 10 or Pest) for a given class."""

import argparse


def to_snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    import re
    s = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", name)
    return s.lower()


def generate_phpunit(
    name: str,
    methods: list[str],
    namespace: str | None,
) -> str:
    test_ns = f"{namespace}\\Tests" if namespace else "Tests"
    subject_ns = f"use {namespace}\\{name};" if namespace else ""

    lines: list[str] = [
        "<?php",
        "declare(strict_types=1);",
        "",
        f"namespace {test_ns};",
        "",
        "use PHPUnit\\Framework\\Attributes\\CoversClass;",
        "use PHPUnit\\Framework\\Attributes\\Test;",
        "use PHPUnit\\Framework\\TestCase;",
    ]

    if subject_ns:
        lines.append(subject_ns)

    lines += [
        "",
        f"#[CoversClass({name}::class)]",
        f"final class {name}Test extends TestCase",
        "{",
        f"    private {name} $sut;",
        "",
        "    protected function setUp(): void",
        "    {",
        f"        $this->sut = new {name}(",
        "            // TODO: inject mocks",
        "            // $this->createMock(SomeDependency::class),",
        "        );",
        "    }",
    ]

    for method in methods:
        snake = to_snake(method)
        lines += [
            "",
            "    #[Test]",
            f"    public function it_{snake}(): void",
            "    {",
            "        // Arrange",
            "        // ...",
            "",
            "        // Act",
            f"        $result = $this->sut->{method}();",
            "",
            "        // Assert",
            "        self::assertNotNull($result);",
            "    }",
        ]

    lines += ["}", ""]
    return "\n".join(lines)


def generate_pest(
    name: str,
    methods: list[str],
    namespace: str | None,
) -> str:
    subject_use = f"use {namespace}\\{name};" if namespace else ""

    lines: list[str] = [
        "<?php",
        "declare(strict_types=1);",
    ]

    if subject_use:
        lines += ["", subject_use]

    lines += [
        "",
        f"describe('{name}', function (): void {{",
    ]

    for method in methods:
        snake = to_snake(method)
        lines += [
            f"    it('{snake}', function (): void {{",
            f"        $sut = new {name}();",
            "",
            f"        $result = $sut->{method}();",
            "",
            "        expect($result)->not->toBeNull();",
            "    });",
            "",
        ]

    lines += ["});", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a PHP test file for a given class"
    )
    parser.add_argument("name", help="Class name to test (e.g. OrderService)")
    parser.add_argument(
        "-m",
        "--methods",
        nargs="+",
        help="Method names to generate tests for",
    )
    parser.add_argument("-n", "--namespace", help="Namespace of the class under test")
    parser.add_argument(
        "--pest",
        action="store_true",
        help="Generate Pest syntax instead of PHPUnit",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    methods = args.methods or ["execute"]

    if args.pest:
        code = generate_pest(
            name=args.name,
            methods=methods,
            namespace=args.namespace,
        )
    else:
        code = generate_phpunit(
            name=args.name,
            methods=methods,
            namespace=args.namespace,
        )

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
    else:
        print(code)


if __name__ == "__main__":
    main()
