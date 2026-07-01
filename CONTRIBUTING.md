# Contributing to CodeForge

Thank you for your interest in contributing to CodeForge! We welcome contributions of all kinds, including bug fixes, features, documentation, and improvements.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/CodeForge.git
   cd CodeForge
   ```
3. **Create a new branch** for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Configure .env with your MongoDB and API keys
```

## Making Changes

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### Commits

- Use clear, descriptive commit messages
- Prefix commits with: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`
- Examples:
  - `feat: add AI mentor node for hint generation`
  - `fix: resolve JWT token validation error`
  - `docs: update README with setup instructions`

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR:
  ```bash
  cd backend
  pytest
  ```

## Submitting Changes

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub
   - Provide a clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes

3. **Respond to feedback** from reviewers
   - Address comments and suggestions
   - Push additional commits to the same branch

## Pull Request Guidelines

- **Title**: Use clear, descriptive titles following the commit format
- **Description**: Explain what, why, and how
- **Related Issues**: Reference any related issues
- **Screenshots**: Include for UI/UX changes
- **Tests**: Ensure tests pass and add new tests for new features

## Code Review Process

- At least one maintainer review required
- All CI checks must pass
- Feedback will be provided if changes are needed
- Once approved, your PR will be merged

## Areas for Contribution

### High Priority
- Bug fixes and stability improvements
- Documentation updates
- Performance optimizations
- Test coverage expansion

### Features
- New problem domains
- Enhanced AI mentor capabilities
- UI/UX improvements
- Additional learning paths

### Documentation
- API documentation
- Deployment guides
- Architecture documentation
- Tutorial content

## Reporting Issues

- **Bugs**: Describe steps to reproduce, expected behavior, and actual behavior
- **Features**: Explain the use case and how it would benefit users
- **Documentation**: Point out unclear or missing documentation

## Community

- Be respectful and constructive
- Help other contributors
- Share knowledge and feedback
- Celebrate contributions

## Questions?

- Open an issue with your question
- Tag it with `question` label
- Someone from the team will help

---

Thank you for contributing to CodeForge! 🚀
