# Contributing to IT Automation Toolkit (ITAT)

Thank you for your interest in contributing to **IT Automation Toolkit**! We welcome contributions from developers, DevOps engineers, and system administrators worldwide.

---

## 🛠️ How to Contribute

### 1. Reporting Bugs & Feature Requests

- Use GitHub Issues to report bugs or request new features.
- Please provide as much detail as possible: your Operating System, Python version, terminal output, and steps to reproduce.

### 2. Developing New Features or Skills

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/it-automation-toolkit.git
   cd it-automation-toolkit
   ```
3. **Create a new branch**:
   ```bash
   git checkout -b feature/my-new-skill
   ```
4. **Set up virtual environment & install in editable mode**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```
5. **Implement your changes and write unit tests** under `tests/`.
6. **Run the test suite**:
   ```bash
   pytest tests/
   ```
7. **Commit your changes**:
   ```bash
   git commit -m "feat(skills): add PostgreSQL support skill"
   ```
8. **Push to your fork and submit a Pull Request (PR)** against the `main` branch.

---

## 📝 Code Style & Conventions

- Follow **PEP 8** style guidelines for Python code.
- Write clear docstrings for all classes and public methods.
- Keep dependencies minimal (prefer Python standard library or existing lightweight dependencies like `psutil`).
- Ensure all custom skills inherit from `BaseSkill` in `itat.skills.base`.

---

## 📜 Code of Conduct

Please be respectful, collaborative, and constructive when interacting with other contributors and maintainers.
