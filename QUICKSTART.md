# Quick Start Guide - Agency-Code (aria)

**Requirements**: Python 3.13 (Python 3.14 not supported yet)

---

## Windows Installation

```powershell
# 1. Install dependencies
python -m pip install git+https://github.com/VRSEN/agency-swarm.git@main
python -m pip install agency-code

# 2. Create .env file with your API key (get from https://console.anthropic.com/settings/keys)
"ANTHROPIC_API_KEY=sk-ant-your_key_here" | Out-File -FilePath .env -Encoding ASCII

# 3. Run aria
aria
```

### If `aria` command not found on Windows:
```powershell
# Option 1: Add to PATH (restart terminal after)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python313\Scripts", "User")

# Option 2: Run with python
python -m agency
```

---

## Mac/Linux Installation

```bash
# 1. Install dependencies
pip install git+https://github.com/VRSEN/agency-swarm.git@main
pip install agency-code

# 2. Create .env file with your API key (get from https://console.anthropic.com/settings/keys)
echo "ANTHROPIC_API_KEY=sk-ant-your_key_here" > .env

# 3. Run aria
aria
```

### If `aria` command not found on Mac/Linux:
```bash
# Option 1: Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# For Mac with zsh:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Option 2: Run with python
python -m agency
```

---

## Python 3.14 Users

If you have Python 3.14, install Python 3.13 first from https://www.python.org/downloads/

Then use:

**Windows**:
```powershell
py -3.13 -m pip install git+https://github.com/VRSEN/agency-swarm.git@main
py -3.13 -m pip install agency-code
py -3.13 -m agency
```

**Mac/Linux**:
```bash
python3.13 -m pip install git+https://github.com/VRSEN/agency-swarm.git@main
python3.13 -m pip install agency-code
python3.13 -m agency
```

---

## Common Commands

| Task | Windows | Mac/Linux |
|------|---------|-----------|
| **Install** | `python -m pip install agency-code` | `pip install agency-code` |
| **Update** | `python -m pip install --upgrade agency-code` | `pip install --upgrade agency-code` |
| **Uninstall** | `python -m pip uninstall agency-code` | `pip uninstall agency-code` |
| **Run** | `aria` or `python -m agency` | `aria` or `python -m agency` |
| **Set API Key** | `"ANTHROPIC_API_KEY=sk-ant-..." \| Out-File .env -Encoding ASCII` | `echo "ANTHROPIC_API_KEY=sk-ant-..." > .env` |

---

## Example Usage

```bash
$ aria

[SafeSession] [OK] Session tracking enabled
[SafeSession] Session ID: abc123...

User: Create a FastAPI hello world app
User: Fix the bug in auth.py line 42
User: Refactor the database connection logic
```

---

## Troubleshooting

**Broken pip error**:
```powershell
# Use python -m pip instead
python -m pip install agency-code
```

**Missing API key error**:
```powershell
# Windows: Create .env in current directory
"ANTHROPIC_API_KEY=your_key" | Out-File .env -Encoding ASCII

# Mac/Linux: Create .env in current directory
echo "ANTHROPIC_API_KEY=your_key" > .env
```

**Python 3.14 error**:
```powershell
# Install Python 3.13 and use py -3.13
py -3.13 -m pip install agency-code
py -3.13 -m agency
```

---

## Links

- **Full Installation Guide**: [INSTALL.md](INSTALL.md)
- **Documentation**: [README.md](README.md)
- **Repository**: https://github.com/joeyjoe808/Agent-C
- **Get API Key**: https://console.anthropic.com/settings/keys
- **PyPI Package**: https://pypi.org/project/agency-code/
