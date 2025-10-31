# Quick Start Guide - Agency-Code (aria)

## One-Line Install

```bash
pipx install agency-code
```

## First-Time Setup

```bash
# 1. Create .env file with your API key
echo "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE" > .env

# 2. Run aria
aria
```

Get your API key at: https://console.anthropic.com/settings/keys

---

## Commands Summary

| Task | Command |
|------|---------|
| **Install globally** | `pipx install agency-code` |
| **Install with pip** | `pip install agency-code` |
| **Install from GitHub** | `pipx install git+https://github.com/joeyjoe808/Agent-C.git` |
| **Update** | `pipx upgrade agency-code` |
| **Uninstall** | `pipx uninstall agency-code` |
| **Run** | `aria` |

---

## Developer Install (Local Development)

```bash
# Clone repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

# Install in editable mode
pip install -e ".[dev]"

# Configure
echo "ANTHROPIC_API_KEY=sk-ant-YOUR_KEY" > .env

# Run
aria
```

---

## Configuration (.env file)

```env
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# Optional
USE_SAFE_SESSION=true
MODEL=anthropic/claude-haiku-4-5-20251001
```

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

**Problem: `aria` command not found**

Solution:
```bash
pipx ensurepath
# Then restart your terminal
```

**Problem: API key not found**

Solution: Create `.env` file in the directory where you run `aria`:
```bash
echo "ANTHROPIC_API_KEY=your_key" > .env
```

---

## Links

- **Full Installation Guide**: [INSTALL.md](INSTALL.md)
- **Documentation**: [ASKME.md](ASKME.md)
- **Repository**: https://github.com/joeyjoe808/Agent-C
- **Get API Key**: https://console.anthropic.com/settings/keys
