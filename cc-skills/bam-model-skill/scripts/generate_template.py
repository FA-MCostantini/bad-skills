#!/usr/bin/env python3
"""
Generate a single BAM artifact template.

Creates or regenerates a specific documentation file
from the BAM template library.

Usage:
    python3 generate_template.py <template_name> <output_path> [project_name]

Available templates:
    project, aq_iterations, tech_stack, acceptance_criteria,
    glossario, logging_strategy, test_environment, deploy,
    api_spec, schema_reference, query_reference, explain_test,
    execution_plan, changelog, readme
"""
import os
import sys
import importlib.util


def load_bootstrap_templates():
    """Load templates from bootstrap_bam_project.py."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    bootstrap_path = os.path.join(script_dir, "bootstrap_bam_project.py")

    spec = importlib.util.spec_from_file_location("bootstrap", bootstrap_path)
    bootstrap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bootstrap)

    return {
        "project": bootstrap.PROJECT_TEMPLATE,
        "aq_iterations": bootstrap.AQ_TEMPLATE,
        "tech_stack": bootstrap.TECH_STACK_TEMPLATE,
        "acceptance_criteria": bootstrap.ACCEPTANCE_CRITERIA_TEMPLATE,
        "glossario": bootstrap.GLOSSARIO_TEMPLATE,
        "logging_strategy": bootstrap.LOGGING_STRATEGY_TEMPLATE,
        "test_environment": bootstrap.TEST_ENVIRONMENT_TEMPLATE,
        "deploy": bootstrap.DEPLOY_TEMPLATE,
        "api_spec": bootstrap.API_SPEC_TEMPLATE,
        "schema_reference": bootstrap.SCHEMA_REFERENCE_TEMPLATE,
        "query_reference": bootstrap.QUERY_REFERENCE_TEMPLATE,
        "explain_test": bootstrap.EXPLAIN_TEST_TEMPLATE,
        "execution_plan": bootstrap.EXECUTION_PLAN_TEMPLATE,
        "changelog": bootstrap.CHANGELOG_TEMPLATE,
        "readme": bootstrap.README_TEMPLATE,
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_template.py <template_name> <output_path> [project_name]")
        print("\nAvailable templates:")
        templates = load_bootstrap_templates()
        for name in sorted(templates.keys()):
            print(f"  - {name}")
        sys.exit(1)

    template_name = sys.argv[1].lower()
    output_path = os.path.abspath(sys.argv[2])
    project_name = sys.argv[3] if len(sys.argv) > 3 else "Project"

    templates = load_bootstrap_templates()

    if template_name not in templates:
        print(f"Error: unknown template '{template_name}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(templates.keys()))}", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(output_path):
        response = input(f"{output_path} already exists. Overwrite? [y/N]: ")
        if response.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    content = templates[template_name].format(project_name=project_name)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Generated: {output_path} (template: {template_name})")


if __name__ == "__main__":
    main()
