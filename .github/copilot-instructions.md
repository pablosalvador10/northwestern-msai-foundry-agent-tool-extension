# Copilot Custom Instructions

## Project Overview

This is a **teaching repository** for Northwestern University's MS AI Foundry program. Students learn to build agentic AI systems using Azure services.

## Coding Standards

### Python
- Use **Python 3.11+** features and type hints
- Follow **PEP 8** style guidelines
- Use **docstrings** for all public functions and classes
- Prefer `pathlib.Path` over `os.path` for file operations
- Use **dataclasses** or **Pydantic** for data structures

### Azure Functions
- Use the **v2 programming model** with decorators (`@app.function_name()`)
- Set `http_auth_level=func.AuthLevel.FUNCTION` for production endpoints
- Return JSON responses with proper status codes
- Include comprehensive logging with `logging.info()` and `logging.error()`

### MCP (Model Context Protocol)
- Use `@app.generic_trigger(type="mcpToolTrigger")` for MCP tools
- Define `toolProperties` as JSON schema with `propertyName`, `propertyType`, `description`
- Return JSON-serialized responses from all MCP tools
- Include descriptive `description` parameters to help AI agents understand tool usage

## Code Organization

```
src/
├── abstractions/       # Reusable Azure service wrappers
├── agent_core.py       # Core agent implementation
└── tool_registry/      # MCP servers and tool definitions
    └── mcps/           # MCP server implementations

notebooks/
├── lab1_*.ipynb        # Azure Functions basics
├── lab2_*.ipynb        # Logic Apps integration
├── lab3_*.ipynb        # Single agent tool calling
└── lab4_*.ipynb        # MCP server development

tests/
└── test_*.py           # Pytest test files
```

## Teaching Context

- **Audience**: Graduate students in MS AI program (smart industry professionals)
- **Tone**: Clear, professional, educational
- **Explanations**: Include architecture diagrams, tables, and step-by-step reasoning
- **Examples**: Provide concrete, runnable code examples
- **Why**: Always explain *why* something works, not just *how*

## Testing

- Use **pytest** for all tests
- Use **fixtures** in `conftest.py` for shared setup
- Mock external Azure services in unit tests
- Test both success and error paths

## Documentation

- Use Markdown for all documentation
- Include architecture diagrams using ASCII art or Mermaid
- Add "Key Takeaways" sections to summarize concepts
- Link to official Microsoft documentation where appropriate

## Dependencies

Core packages for this project:
- `azure-functions` - Azure Functions SDK
- `azure-identity` - Azure authentication
- `azure-ai-projects` - AI Foundry SDK
- `openai` - OpenAI API client
- `pytest` - Testing framework
- `requests` - HTTP client

## Commit Messages

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
