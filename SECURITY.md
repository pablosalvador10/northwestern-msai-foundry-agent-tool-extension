# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability within this project, please follow these steps:

1. **Do not** open a public issue
2. Send an email to the maintainers with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

## Security Best Practices

When using this project:

### Credentials Management

- **Never commit secrets** to the repository
- Use `.env` files for local development (they are gitignored)
- Use Azure Key Vault or similar services in production
- Rotate credentials regularly

### Azure Resources

- Follow the principle of least privilege
- Use managed identities where possible
- Enable Azure security features (e.g., Azure Defender)
- Monitor and audit access logs

### Code Security

- Keep dependencies updated
- Review code for injection vulnerabilities
- Validate all input data
- Use parameterized queries for any database operations

## Dependencies

This project uses automated dependency scanning. To check for vulnerabilities:

```bash
pip install safety
safety check
```

## Contact

For security concerns, please contact the maintainers directly.
