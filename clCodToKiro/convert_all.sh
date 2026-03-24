#!/bin/bash
# Convert all Claude Code skills to Kiro format

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Converting all Claude Code skills to Kiro format..."
echo ""

# Array of skills to convert: source_dir:target_dir:skill_name
SKILLS=(
    "php82-dev-skill:kiro-skills/php82-dev:php82-dev"
    "go-dev-skill:kiro-skills/go-dev:go-dev"
    "ts-vue-dev-skill:kiro-skills/ts-vue-dev:ts-vue-dev"
    "postgresql16-dev-skill:kiro-skills/postgresql16-dev:postgresql16-dev"
    "project-dev-skill:kiro-skills/project-dev:project-dev"
    "ears-doc-skill:kiro-skills/ears-doc:ears-doc"
)

SUCCESS=0
FAILED=0

for skill in "${SKILLS[@]}"; do
    IFS=':' read -r source target name <<< "$skill"
    
    if [ ! -d "$source" ]; then
        echo "⚠️  Skipping $name (source not found: $source)"
        ((FAILED++))
        continue
    fi
    
    echo "Converting: $name"
    if ./convert_skill.py "$source" "$target" "$name"; then
        echo "✅ $name converted successfully"
        ((SUCCESS++))
    else
        echo "❌ $name conversion failed"
        ((FAILED++))
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Conversion Summary:"
echo "  ✅ Successful: $SUCCESS"
echo "  ❌ Failed: $FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo "🎉 All skills converted successfully!"
    echo ""
    echo "Next steps:"
    echo "  1. Review conversion reports in kiro-skills/*/CONVERSION_REPORT.md"
    echo "  2. Test skills with Kiro: read_memory <skill-name>/core-rules"
    echo "  3. Initialize LSP in your projects: /code init"
else
    exit 1
fi
