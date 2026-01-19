# Contributing to Northwestern MSAI Foundry Agent Extension

Thank you for your interest in contributing to this educational project! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Azure subscription (for integration testing)
- Azure Functions Core Tools (optional, for local function development)

### Setting Up Your Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pablosalvador10/northwestern-msai-foundry-agent-extension.git
   cd northwestern-msai-foundry-agent-extension
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   make install-dev
   ```

4. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure credentials
   ```

## Code Standards

### Style Guidelines

- **PEP 8**: Follow PEP 8 style guidelines
- **Type hints**: Use type hints for all function parameters and return values
- **Docstrings**: Write docstrings for all public functions and classes
- **No print statements**: Use structured logging instead

### Linting and Formatting

Run these commands before committing:

```bash
# Format code
make format

# Run linters
make lint
```

### Testing

Write tests for all new functionality:

```bash
# Run tests
make test

# Run tests with coverage
make test-cov
```

## Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code standards
3. **Add or update tests** as needed
4. **Update documentation** if you're changing functionality
5. **Run linting and tests** to ensure everything passes
6. **Submit a pull request** with a clear description

### PR Title Format

Use conventional commit format:
- `feat: add new feature`
- `fix: fix bug in X`
- `docs: update documentation`
- `test: add tests for X`
- `refactor: refactor X`

## Reporting Issues

When reporting issues, please include:

1. **Description** of the issue
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (Python version, OS, etc.)

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Reach out to the maintainers

Thank you for contributing!
