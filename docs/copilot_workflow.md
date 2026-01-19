# GitHub Copilot Workflow Guide

This guide explains how to effectively use GitHub Copilot when working with this repository.

## Overview

GitHub Copilot can significantly accelerate your development workflow for this project. This guide provides tips and prompts for common tasks.

## Setting Up Copilot

1. **Install GitHub Copilot** extension in VS Code or your preferred IDE
2. **Sign in** with your GitHub account
3. **Enable** Copilot for this workspace

## Effective Prompts for This Repo

### Creating New Tools

When adding a new Azure Function tool:

```python
# Create a new tool definition for [describe the function]
# The function should:
# - Be at endpoint: /api/[endpoint]
# - Accept parameters: [list params]
# - Return: [describe response]
```

### Writing Tests

When writing tests, provide context:

```python
# Write pytest tests for [module/function name]
# Test cases should include:
# - Success case
# - Error handling
# - Edge cases for [specific scenarios]
```

### Adding Integrations

For new integration clients:

```python
# Create an async HTTP client for [service name]
# The client should:
# - Use httpx for HTTP requests
# - Include retry logic using tenacity
# - Handle errors with custom exceptions
# - Log operations using structured logging
```

## Copilot Chat Commands

Use Copilot Chat for interactive assistance:

### Explain Code
```
/explain what does the FoundryAgent.run() method do?
```

### Fix Issues
```
/fix the type error in this function
```

### Generate Documentation
```
/doc generate docstring for this function
```

### Write Tests
```
/tests write unit tests for the AzureFunctionsClient class
```

## Best Practices

### 1. Provide Context

Include relevant imports and type hints to help Copilot understand the codebase:

```python
from northwestern_foundry_agent.utils.errors import FoundryAgentError
from northwestern_foundry_agent.utils.logging import get_logger

logger = get_logger(__name__)

# Now write a function that validates configuration...
```

### 2. Use Descriptive Comments

Be specific about requirements:

```python
# Validate the Azure connection string format
# Requirements:
# - Must start with "Endpoint="
# - Must contain "Key=" section
# - Raise ConfigurationError if invalid
def validate_connection_string(conn_str: str) -> bool:
```

### 3. Reference Existing Patterns

Point to existing code for consistency:

```python
# Similar to AzureFunctionsClient in integrations/azure_functions/client.py
# Create a client for Azure Cognitive Services
```

### 4. Iterate on Suggestions

If the first suggestion isn't quite right:
- Press `Alt+]` to see alternative suggestions
- Add more context in comments
- Accept partial suggestions and refine

## Common Tasks

### Adding a New Function to Azure Functions

1. Open `functions/function_app.py`
2. Add comment describing the function:

```python
# HTTP trigger function for [purpose]
# Method: [GET/POST]
# Parameters: [list]
# Returns: JSON with [fields]
@app.route(route="[endpoint]", methods=["[METHOD]"])
def [function_name](req: func.HttpRequest) -> func.HttpResponse:
```

### Creating a Pydantic Model

```python
# Pydantic model for [describe the data]
# Fields:
# - field1: type - description
# - field2: type - description (optional)
class [ModelName](BaseModel):
```

### Adding Error Handling

```python
# Add error handling following the pattern in utils/errors.py
# Should catch [specific errors] and raise [custom exception]
```

## Copilot in Notebooks

When working in Jupyter notebooks:

### Cell Documentation
```python
# %% [markdown]
# ## Step 1: [Description]
# 
# This cell demonstrates how to [task].
# 
# **Expected output:** [describe]
```

### Code Generation
```python
# Create an agent, register tools, and run a sample query
# Use the health_check and quote_of_the_day functions
```

## Troubleshooting

### Copilot Not Suggesting

1. Check if Copilot is enabled for this file type
2. Ensure you're signed in
3. Add more context (imports, type hints)

### Suggestions Don't Match Project Style

1. Add project-specific comments
2. Reference existing code patterns
3. Use `/explain` to understand what Copilot is suggesting

### Getting Better Suggestions

1. Write clear, descriptive comments
2. Include type hints
3. Keep functions small and focused
4. Use meaningful variable names

## Resources

- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [VS Code Copilot Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot)
- [Copilot Chat](https://docs.github.com/en/copilot/github-copilot-chat)
