# Installation & Publishing Guide for Agency-Code (aria)

This guide shows you how to:
1. Install aria locally for development
2. Publish to PyPI for public installation
3. Install aria globally on any machine

---

## Quick Install (After Publishing)

Once published to PyPI, users can install with a single command:

```bash
# Using pip
pip install agency-code

# Using pipx (recommended for CLI tools - installs in isolated environment)
pipx install agency-code
```

Then run from anywhere:
```bash
aria
```

---

## Development Installation

### Step 1: Install in Editable Mode

From the project root directory:

```bash
# Install in editable/development mode
pip install -e .

# Or with development dependencies (includes pytest)
pip install -e ".[dev]"
```

This creates the `aria` command that points to your local code. Changes to the code are immediately reflected.

### Step 2: Configure API Key

```bash
# Create .env file in your working directory (or project root)
echo "ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx" > .env
```

### Step 3: Run

```bash
aria
```

---

## Publishing to PyPI

### Prerequisites

1. **Create PyPI Account**
   - Go to https://pypi.org/account/register/
   - Verify your email
   - Enable 2FA (required for new projects)

2. **Create API Token**
   - Go to https://pypi.org/manage/account/token/
   - Create a token with "Entire account" scope
   - Save the token (starts with `pypi-`)

3. **Install Build Tools**
   ```bash
   pip install --upgrade build twine
   ```

### Publishing Steps

#### Step 1: Update Version Number

Edit [pyproject.toml](pyproject.toml):
```toml
[project]
version = "1.0.1"  # Increment version
```

#### Step 2: Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info

# Windows:
# rmdir /s /q dist build
# del /s /q *.egg-info
```

#### Step 3: Build the Package

```bash
python -m build
```

This creates:
- `dist/agency_code-1.0.0.tar.gz` (source distribution)
- `dist/agency_code-1.0.0-py3-none-any.whl` (wheel distribution)

#### Step 4: Test Upload to TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ agency-code
```

#### Step 5: Upload to PyPI

```bash
python -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token (pypi-...)

#### Step 6: Verify Installation

```bash
# Install from PyPI
pip install agency-code

# Or with pipx
pipx install agency-code

# Run
aria
```

---

## Alternative: Install from GitHub

Users can install directly from your GitHub repository:

```bash
# Install latest from main branch
pip install git+https://github.com/joeyjoe808/Agent-C.git

# Or with pipx
pipx install git+https://github.com/joeyjoe808/Agent-C.git
```

---

## Installation Methods Comparison

| Method | Command | Use Case |
|--------|---------|----------|
| **PyPI** | `pip install agency-code` | Production/stable releases |
| **pipx** | `pipx install agency-code` | Best for CLI tools (isolated) |
| **GitHub** | `pip install git+https://...` | Latest development version |
| **Editable** | `pip install -e .` | Local development |

---

## Troubleshooting

### Issue: `aria` command not found

**Solution 1**: Ensure pip's bin directory is in PATH
```bash
# Find where pip installs scripts
python -m site --user-base

# Add to PATH (example for Unix):
export PATH="$HOME/.local/bin:$PATH"

# Windows:
# Add C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\Scripts to PATH
```

**Solution 2**: Use pipx instead
```bash
pipx install agency-code
pipx ensurepath  # Adds pipx bin to PATH
```

### Issue: Missing dependencies during build

```bash
# Upgrade build tools
pip install --upgrade pip setuptools wheel build

# Install git dependencies manually first
pip install git+https://github.com/VRSEN/agency-swarm.git@main
pip install git+https://github.com/openai/openai-agents-python.git@main
```

### Issue: ANTHROPIC_API_KEY not found

The `.env` file must be in the directory where you run `aria`:

```bash
# Create .env in your working directory
cd ~/projects/my-project
echo "ANTHROPIC_API_KEY=sk-ant-xxxxx" > .env
aria
```

Or set as environment variable:
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
aria
```

---

## Post-Installation Configuration

### Optional: Set Default Model

Edit your `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
MODEL=anthropic/claude-sonnet-4-20250514
USE_SAFE_SESSION=true
```

### Optional: Disable Safety Session

```env
USE_SAFE_SESSION=false
```

---

## Updating the Package

### For Users

```bash
# Update to latest version
pip install --upgrade agency-code

# With pipx
pipx upgrade agency-code
```

### For Developers

1. Make your changes
2. Update version in `pyproject.toml`
3. Commit changes: `git commit -am "Version bump to X.Y.Z"`
4. Tag release: `git tag vX.Y.Z`
5. Push: `git push && git push --tags`
6. Build and publish: `python -m build && python -m twine upload dist/*`

---

## Automation with GitHub Actions

You can automate publishing with GitHub Actions. Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

Add your PyPI token as a GitHub secret named `PYPI_API_TOKEN`.

---

## Summary

**For Users:**
```bash
pipx install agency-code
echo "ANTHROPIC_API_KEY=sk-ant-xxx" > .env
aria
```

**For Developers:**
```bash
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C
pip install -e ".[dev]"
echo "ANTHROPIC_API_KEY=sk-ant-xxx" > .env
aria
```

**For Publishing:**
```bash
# Bump version in pyproject.toml
python -m build
python -m twine upload dist/*
```

---

## Links

- **PyPI Project Page**: https://pypi.org/project/agency-code/ (after publishing)
- **GitHub Repository**: https://github.com/joeyjoe808/Agent-C
- **PyPI Help**: https://packaging.python.org/tutorials/packaging-projects/
- **pipx Documentation**: https://pipx.pypa.io/
