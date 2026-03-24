# AI Agent Usage Examples

## Example 1: Standard Skill (Fast Path)

```bash
# Use rule-based script for known structure
./convert_skill.py ./php82-dev-skill ./kiro-skills/php82-dev php82-dev
```

## Example 2: Complex/Unknown Skill (AI Path)

### In Kiro:

```
# Load AI agent
read_file ai-converter-agent.md

# Convert with deep analysis
Convert ./custom-complex-skill to ./kiro-skills/custom-complex custom-complex

# Agent will:
# 1. Read and analyze all files
# 2. Understand script logic by reading code
# 3. Classify based on content, not filename
# 4. Document reasoning for each decision
# 5. Generate optimized structure
```

## Example 3: Skill from Internet (Unknown Structure)

```
# Download skill
git clone https://github.com/someone/awesome-skill ./awesome-skill

# In Kiro with AI agent loaded
Convert ./awesome-skill to ./kiro-skills/awesome analyzing deeply

# Agent adapts to any structure:
# - Non-standard directory layout
# - Custom script purposes
# - Unique reference organization
# - Different metadata format
```

## Example 4: Interactive Review

```
# In Kiro
read_file ai-converter-agent.md

Analyze ./new-skill and show me classification decisions before generating output

# Agent will:
# 1. Analyze skill
# 2. Present classification table with reasoning
# 3. Wait for your approval
# 4. Generate after confirmation
```

## Comparison

| Scenario | Tool | Why |
|----------|------|-----|
| PHP/Go/TS skills (standard) | `convert_skill.py` | Fast, known structure |
| Batch conversion | `convert_all.sh` | Automate multiple |
| Downloaded from internet | AI agent in Kiro | Unknown structure |
| Custom/complex logic | AI agent in Kiro | Needs content analysis |
| Want detailed reasoning | AI agent in Kiro | Documents decisions |
