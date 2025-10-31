# Publishing Agency-Code to PyPI

This guide walks you through publishing your package to PyPI so users can install it with `pipx install agency-code`.

---

## One-Time Setup

### 1. Create PyPI Account

1. Go to https://pypi.org/account/register/
2. Verify your email
3. Enable 2FA (required for publishing)

### 2. Create API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: "agency-code-upload" (or whatever you want)
4. Scope: "Entire account" (or create project-specific token later)
5. **SAVE THE TOKEN** - you can only see it once! (starts with `pypi-`)

### 3. Install Build Tools

```bash
# In your virtual environment
pip install --upgrade build twine
```

---

## Publishing Steps

### Step 1: Update Version Number

Edit `pyproject.toml` and increment the version:

```toml
[project]
version = "1.0.1"  # Change this (was 1.0.0)
```

Version format: `MAJOR.MINOR.PATCH`
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Step 2: Clean Old Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info

# Windows PowerShell:
# Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue
```

### Step 3: Build the Package

```bash
python -m build
```

This creates:
- `dist/agency_code-1.0.0.tar.gz` (source)
- `dist/agency_code-1.0.0-py3-none-any.whl` (wheel)

### Step 4: Upload to PyPI

```bash
python -m twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your PyPI token (paste the `pypi-...` token)

### Step 5: Verify

```bash
# Wait 1-2 minutes, then test install
pip install agency-code

# Or with pipx
pipx install agency-code

# Test it works
aria
```

---

## Testing Before Publishing (Recommended)

### Use TestPyPI First

TestPyPI is a separate instance for testing:

1. Create account at https://test.pypi.org/account/register/
2. Create token at https://test.pypi.org/manage/account/token/

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ agency-code

# If it works, upload to real PyPI
python -m twine upload dist/*
```

---

## Automation (Optional)

### Save PyPI Token for Easy Upload

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-your-token-here

[testpypi]
username = __token__
password = pypi-your-test-token-here
```

**Important**: Keep this file secure! Add to `.gitignore`.

Now you can upload without entering credentials:

```bash
python -m twine upload dist/*
```

---

## Complete Publishing Workflow

Here's the full workflow when releasing a new version:

```bash
# 1. Make your changes and test
pytest tests/ -v

# 2. Update version in pyproject.toml
# Edit: version = "1.0.1"

# 3. Commit changes
git add .
git commit -m "Release v1.0.1: Description of changes"
git tag v1.0.1
git push origin main --tags

# 4. Clean and build
rm -rf dist/ build/ *.egg-info
python -m build

# 5. Upload to PyPI
python -m twine upload dist/*

# 6. Test installation
pipx install agency-code --force
aria
```

---

## GitHub Actions Automation

You can automate publishing with GitHub Actions when you create a release.

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install --upgrade pip build twine

      - name: Build package
        run: python -m build

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Then add your PyPI token as a GitHub secret:
1. Go to your repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your `pypi-...` token

Now when you create a GitHub release, it will automatically publish to PyPI!

---

## Troubleshooting

### Error: "File already exists"

You can't re-upload the same version. Increment the version number in `pyproject.toml`.

### Error: "Invalid credentials"

- Username must be `__token__` (not your PyPI username)
- Password must be your API token starting with `pypi-`

### Error: "Package name already taken"

Change the package name in `pyproject.toml`:
```toml
name = "agency-code-yourname"  # Make it unique
```

### Error: "403 Forbidden"

You need to enable 2FA on your PyPI account.

---

## After Publishing

### Update Documentation

Once published, update these files to reflect the PyPI package:
- ✅ README.md (already updated with `pipx install agency-code`)
- Check INSTALL.md
- Check QUICKSTART.md

### Announce

- Tweet/post about the release
- Update your GitHub repo description
- Add PyPI badge to README:

```markdown
[![PyPI version](https://badge.fury.io/py/agency-code.svg)](https://badge.fury.io/py/agency-code)
[![Downloads](https://pepy.tech/badge/agency-code)](https://pepy.tech/project/agency-code)
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Build** | `python -m build` |
| **Upload to PyPI** | `python -m twine upload dist/*` |
| **Upload to TestPyPI** | `python -m twine upload --repository testpypi dist/*` |
| **Clean builds** | `rm -rf dist/ build/ *.egg-info` |
| **Check package** | `twine check dist/*` |

---

## Links

- **PyPI**: https://pypi.org/
- **TestPyPI**: https://test.pypi.org/
- **Packaging Tutorial**: https://packaging.python.org/tutorials/packaging-projects/
- **Your Package** (after publishing): https://pypi.org/project/agency-code/
