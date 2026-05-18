# Contributing to Aletheia Python SDK

Thank you for considering contributing to Aletheia AI Python SDK!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aletheia-ai/python-sdk.git
   cd python-sdk
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   pytest
   ```

## Development Workflow

### Before committing:

1. **Format code:**
   ```bash
   black aletheia/ tests/ examples/
   ```

2. **Lint:**
   ```bash
   ruff check aletheia/ tests/
   mypy aletheia/
   ```

3. **Run tests:**
   ```bash
   pytest --cov=aletheia
   ```

### Code Style

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

### Commit Messages

Use conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test updates
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

Examples:
```
feat(agents): add batch registration method
fix(audit): handle missing timestamp proof
docs(readme): add async client examples
```

## Pull Request Process

1. Fork the repository
2. Create feature branch: `git checkout -b feat/my-feature`
3. Make changes and commit
4. Push to your fork: `git push origin feat/my-feature`
5. Create Pull Request

### PR Checklist:

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black`)
- [ ] Linting passes (`ruff`, `mypy`)
- [ ] Documentation updated (if needed)
- [ ] Examples added (for new features)
- [ ] CHANGELOG.md updated

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

Requires running Aletheia backend:

```bash
# Terminal 1: Start backend
cd ../../backend
./mvnw spring-boot:run

# Terminal 2: Run integration tests
pytest tests/integration/
```

### Coverage

```bash
pytest --cov=aletheia --cov-report=html
open htmlcov/index.html
```

## Documentation

Update documentation for:
- New API methods
- Changed behavior
- New examples
- Configuration options

Documentation lives in:
- `README.md` - Main documentation
- `examples/` - Usage examples
- Docstrings - In-code documentation

## Release Process

(For maintainers)

1. Update version in `setup.py` and `aletheia/__init__.py`
2. Update `CHANGELOG.md`
3. Create release commit: `git commit -m "chore: release v0.2.0"`
4. Tag release: `git tag v0.2.0`
5. Push: `git push && git push --tags`
6. Build and publish:
   ```bash
   python -m build
   python -m twine upload dist/*
   ```

## Questions?

- Open an issue
- Join Discord: https://discord.gg/aletheia-ai
- Email: dev@aletheia.ai
