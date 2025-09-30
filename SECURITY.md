# Security Policy

## Supported Versions

We actively support the following versions of CloudDojo:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in CloudDojo, please report it responsibly.

### How to Report

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email us at: datakaitechnologies@gmail.com
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We'll acknowledge receipt within 48 hours
- **Assessment**: We'll assess the vulnerability within 5 business days
- **Updates**: We'll provide regular updates on our progress
- **Resolution**: We'll work to resolve critical issues within 30 days

### Security Considerations

CloudDojo scenarios may involve:
- Docker containers with elevated privileges
- Kubernetes cluster access
- Network configurations
- File system access

### Best Practices for Contributors

When creating scenarios:
- Avoid hardcoded secrets or credentials
- Use minimal required permissions
- Validate user inputs
- Document security implications
- Test in isolated environments

### Responsible Disclosure

We follow responsible disclosure practices:
- We'll work with you to understand and resolve the issue
- We'll credit you in our security advisories (if desired)
- We'll coordinate public disclosure timing
- We'll provide security updates to users

Thank you for helping keep CloudDojo secure! 🔒