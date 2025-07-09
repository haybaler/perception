# Contributing to URL Scanner for Google Search Console

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/url-scanner-gsc.git
   cd url-scanner-gsc
   ```
3. Create a branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

1. Set up Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Install development dependencies:
   ```bash
   pip install pytest black flake8
   ```

3. Run tests:
   ```bash
   python -m pytest
   ```

## Code Style

- Follow PEP 8 for Python code
- Use Black for code formatting: `black .`
- Run flake8 for linting: `flake8 .`
- Keep line length under 88 characters (Black's default)
- Write clear, descriptive variable and function names

## Making Changes

1. **Write tests** for new functionality
2. **Update documentation** if needed
3. **Follow existing patterns** in the codebase
4. **Keep commits focused** - one feature/fix per commit
5. **Write clear commit messages**:
   ```
   Add support for bulk URL analysis
   
   - Implement batch processing endpoint
   - Add progress tracking for large batches
   - Update frontend to show batch status
   ```

## Submitting Pull Requests

1. Push your changes to your fork
2. Submit a pull request to the main repository
3. Include:
   - Clear description of changes
   - Any related issue numbers
   - Screenshots for UI changes
   - Test results

## Pull Request Guidelines

- **One feature per PR** - keep PRs focused
- **Include tests** - all new code needs tests
- **Update docs** - keep documentation current
- **Pass CI checks** - ensure all tests pass
- **Request review** - tag maintainers when ready

## Reporting Issues

When reporting issues, include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

## Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Describe the use case
- Explain expected behavior
- Consider implementation approach

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive criticism
- Assume positive intent

## Areas for Contribution

### High Priority
- Google Search Console API integration
- Performance optimizations
- Additional analysis engines
- Test coverage improvements

### Good First Issues
- Documentation improvements
- Bug fixes in analysis engines
- UI/UX enhancements
- Adding type hints

### Future Features
- Scheduled monitoring
- Competitor analysis
- PDF report generation
- Multi-language support

## Questions?

Feel free to:
- Open a discussion on GitHub
- Check existing issues
- Review the wiki

Thank you for contributing to make this tool better for everyone!