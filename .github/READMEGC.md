# GitHub Copilot Configuration

This folder contains custom instructions and Agent Skills to tailor GitHub Copilot for this project.

## Files Overview

```
.github/
├── copilot-instructions.md    # Always-on coding standards
├── README.md                  # This file
└── skills/                    # Agent Skills (loaded on-demand)
    ├── agentic-ai/
    ├── azure-functions/
    ├── mcp-server/
    ├── notebook-development/
    └── python-testing/
```

## Custom Instructions

**File:** `copilot-instructions.md`

These instructions are **always applied** to every Copilot interaction. They define:
- Python coding standards (type hints, PEP 8)
- Azure Functions patterns (v2 model)
- MCP conventions
- Teaching context for graduate students

## Agent Skills

Skills are **loaded on-demand** when relevant to your prompt.

| Skill | When Copilot Uses It |
|-------|---------------------|
| `azure-functions` | Creating/debugging Azure Functions |
| `mcp-server` | Building MCP tools, configuring clients |
| `python-testing` | Writing pytest tests |
| `agentic-ai` | Building AI agents with tool calling |
| `notebook-development` | Creating teaching lab notebooks |

### Enable Skills

1. Open VS Code Settings (`Cmd+,`)
2. Search: `chat.useAgentSkills`
3. Enable the checkbox

### How Skills Work

1. **Discovery** - Copilot reads skill names/descriptions (lightweight)
2. **Loading** - When your prompt matches, the full `SKILL.md` loads
3. **Resources** - Additional files in skill folders load as needed

## Adding a New Skill

1. Create a folder: `.github/skills/my-skill/`
2. Add `SKILL.md` with this format:

```markdown
---
name: my-skill
description: When to use this skill (helps Copilot decide)
---

# Skill Title

Instructions, patterns, and examples...
```

3. Optionally add scripts, templates, or examples to the folder

## Testing Your Setup

Ask Copilot in Agent Mode:
- "Create an Azure Function" → Should use `azure-functions` skill
- "Write tests for this" → Should use `python-testing` skill
- "Create a new lab notebook" → Should use `notebook-development` skill

## Resources

- [Agent Skills Docs](https://code.visualstudio.com/docs/copilot/copilot-customization)
- [Custom Instructions](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)
- [Agent Skills Standard](https://agentskills.io)
