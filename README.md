# Agency-Code: AI Developer Agent

**An intelligent AI development assistant powered by Claude with built-in safety architecture.**

> **Forked from**: [VRSEN/Agency-Code](https://github.com/VRSEN/Agency-Code.git)
> Enhanced with production-ready safety guardrails, auto-termination, and webhook integration.

**Key Features**: Multi-agent system (Coder + Planner) • Timeout monitoring • Runaway detection • WebSearch/WebFetch intelligence • Webhook-ready hooks • 181+ tests

📖 **For detailed documentation, architecture, and integration examples**, see [ASKME.md](ASKME.md)

---

## ⚡ Quick Install (Recommended)

Install globally with a single command:

```bash
# Install with pipx (recommended - isolated environment)
pipx install agency-code

# Or with pip
pip install agency-code
```

Configure your API key:

```bash
# Create .env file in your working directory
echo "ANTHROPIC_API_KEY=sk-ant-your_key_here" > .env
```

Run from anywhere:

```bash
aria
```

Get your API key: https://console.anthropic.com/settings/keys

---

## 🚀 Manual Installation (Development)

### Prerequisites

- **Python 3.13+**
- **Git**
- **Anthropic API Key** ([Get one here](https://console.anthropic.com/))

### Installation

#### **Mac/Linux**

```bash
# 1. Clone the repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

# 2. Create and activate virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Fix Anthropic compatibility (important!)
pip install git+https://github.com/openai/openai-agents-python.git@main
```

#### **Windows (PowerShell)**

```powershell
# 1. Clone the repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate.ps1

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Fix Anthropic compatibility (important!)
pip install git+https://github.com/openai/openai-agents-python.git@main
```

#### **Windows (Command Prompt)**

```cmd
REM 1. Clone the repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

REM 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

REM 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

REM 4. Fix Anthropic compatibility (important!)
pip install git+https://github.com/openai/openai-agents-python.git@main
```

---

## 🔑 Configuration

### Create `.env` File

The agent looks for a `.env` file in the root directory. Create it with your API key:

**Option 1: Create from scratch**

```bash
# Create .env file
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# On Windows (PowerShell):
# "ANTHROPIC_API_KEY=your_api_key_here" | Out-File -FilePath .env -Encoding ASCII
```

**Option 2: Use example template (if provided)**

```bash
cp .env.example .env
nano .env  # or notepad .env on Windows
```

### `.env` File Contents

```env
# Required: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Enable/disable safety session tracking (default: true)
USE_SAFE_SESSION=true

# Optional: Model selection (default: claude-haiku-4-5)
MODEL=anthropic/claude-haiku-4-5-20251001
```

**Get your API key**: https://console.anthropic.com/settings/keys

---

## ▶️ Run Agency-Code

**If installed via pipx/pip** (Quick Install):

```bash
# Run from anywhere
aria
```

**If installed manually** (Development):

```bash
# Activate virtual environment (if not already activated)
source .venv/bin/activate  # Mac/Linux
# .venv\Scripts\activate     # Windows

# Run the agent
python agency.py
# Or use: aria

# On Mac, use sudo if you get permission errors:
sudo python agency.py
```

**You'll see:**
```
[SafeSession] [OK] Session tracking enabled
[SafeSession] Session ID: abc123...

User: [Type your request here]
```

### Example Requests

```
User: Create a FastAPI hello world app
User: Fix the bug in database.py line 42
User: Research best practices for JWT authentication
User: Help me refactor this function to be more readable
```

---

## 🛡️ Safety Features

**Built-in Protection:**
- ✅ **Timeout Monitoring**: 30min session / 5min turn / 2min tool timeouts
- ✅ **Runaway Detection**: Catches infinite loops (5+ same tool calls)
- ✅ **Auto-Termination**: Optional auto-kill on timeout/runaway (disabled by default)
- ✅ **Graceful Cancellation**: Press Ctrl+C to save state and exit cleanly

**Webhook Integration:**
- ✅ **Hook System**: Triggers on every tool execution and agent handoff
- ✅ **Perfect for APIs**: Use as backend for your web application
- ✅ **Real-time Tracking**: Session metrics (tool calls, duration, reasoning steps)

See [ASKME.md](ASKME.md) for webhook integration examples and detailed safety documentation.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run safety architecture tests (44 tests)
pytest tests/test_session_metrics.py \
       tests/test_safe_session.py \
       tests/test_timeout_monitor.py \
       tests/test_runaway_detector.py \
       tests/test_background_monitor.py \
       tests/test_cancellation.py -v
```

---

## 📂 Project Structure

```
Agency-Code/
├── agency.py                 # Main entry point
├── .env                      # API keys (you create this)
├── requirements.txt          # Dependencies
│
├── agency_code_agent/        # Coder agent
├── planner_agent/            # Planner agent
├── safety/                   # Safety architecture
├── tools/                    # 14+ tool implementations
├── shared/                   # Utilities & hooks
└── tests/                    # 181+ automated tests
```

---

## 🔗 Links

- **Repository**: https://github.com/joeyjoe808/Agent-C
- **Issues**: https://github.com/joeyjoe808/Agent-C/issues
- **Original Fork**: https://github.com/VRSEN/Agency-Code
- **Agency Swarm**: https://agency-swarm.ai/

---

## 📖 Documentation

**For detailed information**, see [ASKME.md](ASKME.md):
- Complete feature documentation
- Webhook integration examples
- Safety architecture details
- API integration patterns
- Demo tasks and examples
- Architecture diagrams

**For developers**, see [AGENTS.md](AGENTS.md):
- Repository structure and guidelines
- Coding style and conventions
- Testing guidelines
- Commit and PR guidelines

---

## 🤝 Contributing

Fully open-source - build, refine, and improve as needed!

1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD)
4. Run test suite
5. Submit pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Questions?** Open an issue or check [ASKME.md](ASKME.md) for detailed docs!
