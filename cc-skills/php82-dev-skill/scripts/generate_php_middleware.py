#!/usr/bin/env python3
"""Generate a PSR-15 Middleware implementation."""

import argparse


# Type-specific stubs: returns (extra_deps, process_body_lines)
STUBS: dict[str, tuple[list[tuple[str, str]], list[str]]] = {
    "auth": (
        [("tokenValidator", "TokenValidatorInterface")],
        [
            "        $token = $request->getHeaderLine('Authorization');",
            "",
            "        if ($token === '') {",
            "            return new JsonResponse(['error' => 'Unauthorized'], 401);",
            "        }",
            "",
            "        try {",
            "            $user = $this->tokenValidator->validate($token);",
            "            $request = $request->withAttribute('user', $user);",
            "        } catch (InvalidTokenException $e) {",
            "            $this->logger->warning('Invalid token', ['error' => $e->getMessage()]);",
            "            return new JsonResponse(['error' => 'Invalid token'], 401);",
            "        }",
            "",
            "        return $handler->handle($request);",
        ],
    ),
    "ratelimit": (
        [("rateLimiter", "RateLimiterInterface")],
        [
            "        $identifier = $request->getServerParams()['REMOTE_ADDR'] ?? 'unknown';",
            "",
            "        if (!$this->rateLimiter->attempt($identifier)) {",
            "            return new JsonResponse(['error' => 'Too Many Requests'], 429);",
            "        }",
            "",
            "        return $handler->handle($request);",
        ],
    ),
    "logging": (
        [],
        [
            "        $method = $request->getMethod();",
            "        $path = (string) $request->getUri()->getPath();",
            "        $start = hrtime(true);",
            "",
            "        $this->logger->info('Request started', [",
            "            'method' => $method,",
            "            'path'   => $path,",
            "        ]);",
            "",
            "        $response = $handler->handle($request);",
            "",
            "        $durationMs = (hrtime(true) - $start) / 1_000_000;",
            "        $this->logger->info('Request completed', [",
            "            'method'      => $method,",
            "            'path'        => $path,",
            "            'status'      => $response->getStatusCode(),",
            "            'duration_ms' => round($durationMs, 2),",
            "        ]);",
            "",
            "        return $response;",
        ],
    ),
    "cors": (
        [],
        [
            "        // Handle preflight",
            "        if ($request->getMethod() === 'OPTIONS') {",
            "            return $this->buildCorsResponse(new Response());",
            "        }",
            "",
            "        $response = $handler->handle($request);",
            "",
            "        return $this->buildCorsResponse($response);",
        ],
    ),
    "generic": (
        [],
        [
            "        // TODO: implement middleware logic",
            "        return $handler->handle($request);",
        ],
    ),
}

CORS_HELPER = """
    private function buildCorsResponse(ResponseInterface $response): ResponseInterface
    {
        return $response
            ->withHeader('Access-Control-Allow-Origin', '*')
            ->withHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
            ->withHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    }
"""


def generate_middleware(
    name: str,
    middleware_type: str,
    namespace: str | None = None,
) -> str:
    extra_deps, process_body = STUBS.get(middleware_type, STUBS["generic"])

    lines: list[str] = [
        "<?php",
        "declare(strict_types=1);",
        "",
    ]

    if namespace:
        lines += [f"namespace {namespace};", ""]

    lines += [
        "use Psr\\Http\\Message\\ResponseInterface;",
        "use Psr\\Http\\Message\\ServerRequestInterface;",
        "use Psr\\Http\\Server\\MiddlewareInterface;",
        "use Psr\\Http\\Server\\RequestHandlerInterface;",
        "use Psr\\Log\\LoggerInterface;",
        "",
        f"final readonly class {name} implements MiddlewareInterface",
        "{",
        "    public function __construct(",
    ]

    for dep_name, dep_type in extra_deps:
        lines.append(f"        private {dep_type} ${dep_name},")

    lines += [
        "        private LoggerInterface $logger,",
        "    ) {",
        "    }",
        "",
        "    public function process(",
        "        ServerRequestInterface $request,",
        "        RequestHandlerInterface $handler,",
        "    ): ResponseInterface {",
    ]

    lines += process_body

    # Add CORS helper if needed
    if middleware_type != "cors":
        lines += [
            "    }",
            "}",
            "",
        ]
    else:
        lines += [
            "    }",
        ]
        # Add CORS helper method
        for helper_line in CORS_HELPER.rstrip("\n").split("\n"):
            lines.append(helper_line)
        lines += [
            "}",
            "",
        ]

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a PSR-15 Middleware implementation"
    )
    parser.add_argument("name", help="Middleware class name (e.g. AuthenticationMiddleware)")
    parser.add_argument(
        "--type",
        choices=["auth", "ratelimit", "logging", "cors", "generic"],
        default="generic",
        help="Middleware type (default: generic)",
    )
    parser.add_argument("-n", "--namespace", help="PHP namespace")
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    code = generate_middleware(
        name=args.name,
        middleware_type=args.type,
        namespace=args.namespace,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(code)
    else:
        print(code)


if __name__ == "__main__":
    main()
