# 🤝 Contributing to WhatMail

Thank you for your interest in contributing to WhatMail! We welcome contributions from everyone.

## 📋 Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)

---

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold this code.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git installed on your machine
- Chrome browser
- Gmail account with App Password
- WhatsApp account

### Fork & Clone
1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/whatmail.git
   cd whatmail
   ```

---

## 🛠 How to Contribute

### Types of Contributions
- 🐛 **Bug Fixes**: Fix issues and improve stability
- ✨ **New Features**: Add new functionality
- 📚 **Documentation**: Improve docs, examples, tutorials
- 🧪 **Testing**: Add or improve test coverage
- 🎨 **UI/UX**: Enhance user interface and experience
- ⚡ **Performance**: Optimize code for better performance

### Before You Start
1. Check existing issues to avoid duplicates
2. Open an issue to discuss major changes
3. Look for issues labeled `good first issue` for beginners

---

## 💻 Development Setup

### 1. Set Up Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

### 3. Set Up Environment
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Run Tests
```bash
python -m pytest tests/
```

### 5. Start Application
```bash
python whatmail_gui.py
```

---

## 📏 Coding Standards

### Python Style Guide
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Maximum line length: 88 characters
- Use meaningful variable and function names

### Code Formatting
```bash
# Format code with black
black .

# Check with flake8
flake8 .

# Type checking with mypy
mypy .
```

### Docstring Format
```python
def process_email(email_content: str, filters: List[str]) -> bool:
    """
    Process email content and check if it matches filters.

    Args:
        email_content: Raw email content to process
        filters: List of keywords to match against

    Returns:
        bool: True if email matches any filter, False otherwise

    Raises:
        ValueError: If email_content is empty

    Example:
        >>> process_email("Urgent meeting", ["urgent", "important"])
        True
    """
    pass
```

---

## 📤 Pull Request Process

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Changes
- Write clean, well-documented code
- Add tests for new functionality  
- Update documentation as needed
- Follow existing code patterns

### 3. Test Your Changes
```bash
# Run all tests
python -m pytest tests/ -v

# Test specific functionality
python test_your_feature.py

# Manual testing
python whatmail_gui.py
```

### 4. Commit Changes
```bash
git add .
git commit -m "feat: add email signature detection

- Implemented regex pattern for signature detection
- Added configuration option for signature removal
- Updated tests and documentation
- Fixes #123"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference related issues (`Fixes #123`)
- Screenshots for UI changes
- Test results summary

### 6. Code Review Process
- Maintainers will review your PR
- Address any feedback promptly
- Make requested changes in new commits
- Once approved, your PR will be merged

---

## 🐛 Issue Guidelines

### Before Opening an Issue
1. Search existing issues first
2. Check the documentation
3. Try the latest version

### Bug Reports
Include:
- **Environment**: OS, Python version, Chrome version
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots**: If applicable
- **Logs**: Relevant error messages

### Feature Requests
Include:
- **Problem**: What problem does this solve?
- **Solution**: Describe your proposed solution
- **Alternatives**: Other solutions you considered
- **Additional Context**: Screenshots, examples, etc.

---

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on
- `duplicate`: This issue already exists

---

## 🧪 Testing Guidelines

### Writing Tests
```python
import pytest
from whatmail.email_processor import EmailProcessor

def test_email_filtering():
    """Test email filtering functionality."""
    processor = EmailProcessor()

    # Test important email detection
    assert processor.is_important("Urgent meeting", ["urgent"])
    assert not processor.is_important("Newsletter", ["urgent"])

def test_html_conversion():
    """Test HTML to text conversion."""
    html = "<h1>Test</h1><p>Content</p>"
    expected = "TEST\n\nContent"

    result = convert_html_to_text(html)
    assert result.strip() == expected
```

### Test Categories
- **Unit Tests**: Test individual functions
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test full workflows
- **Performance Tests**: Test speed and memory usage

---

## 📚 Documentation

### Code Comments
- Explain why, not what
- Use clear, concise language
- Update comments when changing code

### Documentation Updates
When adding features, update:
- README.md with usage examples
- API documentation
- Configuration options
- Troubleshooting guides

---

## 🎯 Development Workflow

### Typical Workflow
1. **Issue Discussion**: Discuss approach in issue comments
2. **Development**: Work on your feature branch
3. **Testing**: Ensure all tests pass
4. **Documentation**: Update relevant docs
5. **Pull Request**: Submit for review
6. **Code Review**: Address feedback
7. **Merge**: Maintainer merges approved PR

### Communication
- Be respectful and constructive
- Ask questions if anything is unclear
- Provide context for your changes
- Respond to feedback promptly

---

## 🏆 Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributors page
- Special thanks in commit messages

---

## 📞 Getting Help

- **General Questions**: Open a GitHub Discussion
- **Bug Reports**: Create an issue with bug template
- **Feature Ideas**: Create an issue with feature template
- **Security Issues**: Email maintainers privately

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to WhatMail! 🚀
