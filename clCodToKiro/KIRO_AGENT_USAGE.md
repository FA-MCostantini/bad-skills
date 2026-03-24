# Kiro Agent Usage Example

## Using the Skill Converter Agent with Kiro

### Method 1: Direct Script Execution (Recommended)

```bash
# Convert single skill
./convert_skill.py ./php82-dev-skill ./kiro-skills/php82-dev php82-dev

# Convert all skills
./convert_all.sh
```

### Method 2: Load Agent as Context in Kiro

1. Start Kiro in this directory
2. Load the agent specification:
   ```
   read_file skill-converter-agent.md
   ```

3. Ask Kiro to convert a skill:
   ```
   Convert the go-dev-skill to Kiro format in ./kiro-skills/go-dev
   ```

The agent will follow the workflow defined in `skill-converter-agent.md`.

### Method 3: Use as Memory

Save the agent as a Kiro memory for reuse:

```bash
# In Kiro
write_memory skills/converter-agent <content of skill-converter-agent.md>

# Later, load when needed
read_memory skills/converter-agent
```

## Verification

After conversion, check:

1. **Structure**:
   ```bash
   tree kiro-skills/<skill-name>
   ```

2. **Conversion Report**:
   ```bash
   cat kiro-skills/<skill-name>/CONVERSION_REPORT.md
   ```

3. **Usage Guide**:
   ```bash
   cat kiro-skills/<skill-name>/USAGE.md
   ```

## Testing Converted Skills

```bash
# In Kiro, in a project directory
/code init
read_memory php82-dev/core-rules
code search_symbols MyClass
```
