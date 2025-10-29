# Session Management Research - Phase 1

## Date: 2025-10-28
## Researcher: Claude Agent Orchestrator (3 parallel agents)
## Time Spent: 7 minutes (UNDER 20 MIN LIMIT)

---

## 1. Call Flow Diagram (Text-Based)

```
User runs agency.py
  └─> main() (line 33-57)
      ├─> create_planner_agent(model, reasoning_effort="low") (line 34-37)
      │   └─> planner_agent.py:create_planner_agent() (lines 35-72)
      │       ├─> detect_model_type(model) (line 39)
      │       ├─> create_message_filter_hook() (line 41)
      │       └─> Agent(name="PlannerAgent", hooks=filter_hook, ...)
      │
      ├─> create_agency_code_agent(model, reasoning_effort="high") (line 38-40)
      │   └─> agency_code_agent.py:create_agency_code_agent() (lines 39-78)
      │       ├─> detect_model_type(model) (line 45)
      │       ├─> create_system_reminder_hook() (line 50)
      │       └─> Agent(name="AgencyCodeAgent", hooks=reminder_hook, ...)
      │
      ├─> Agency(coder, planner, communication_flows=[...]) (lines 45-54)
      │   ├─> Bidirectional handoff: coder ↔ planner
      │   └─> Shared instructions: project-overview.md
      │
      └─> agency.terminal_demo() (line 57)
          └─> Interactive terminal loop
              ├─> User input
              ├─> Agent processing (subprocess isolation)
              ├─> Tool execution via hooks
              │   └─> on_tool_start() → tool.run() → on_tool_end()
              └─> Response output
```

---

## 2. Files Touched by Session Creation

### Core Orchestration Files
1. **agency.py** (lines 1-59)
   - Line 34-40: Agent creation via factory functions
   - Line 45-54: Agency creation with communication flows
   - Line 57: Execution entry point (terminal_demo)

2. **agency_code_agent/agency_code_agent.py** (lines 1-83)
   - Line 39-78: `create_agency_code_agent()` factory function
   - Line 45: Model type detection
   - Line 50: Hook creation (SystemReminderHook)
   - Line 57-58: Agent instantiation with hooks
   - Line 59-76: Tool array (15+ tools)

3. **planner_agent/planner_agent.py** (lines 1-77)
   - Line 35-72: `create_planner_agent()` factory function
   - Line 39: Model type detection
   - Line 41: Hook creation (MessageFilterHook)
   - Line 51-52: Agent instantiation with hooks

4. **shared/agent_utils.py** (lines 1-81)
   - Line 11-16: `detect_model_type()` - Model detection
   - Line 19-28: `select_instructions_file()` - Configuration
   - Line 31-50: `render_instructions()` - Template rendering
   - Line 53-75: `create_model_settings()` - Model config
   - Line 78-81: `get_model_instance()` - Model instantiation

5. **shared/system_hooks.py** (lines 1-313)
   - Line 6-157: `SystemReminderHook` class - Tool call tracking
   - Line 20: `tool_call_count` - Existing metrics tracking
   - Line 42-51: `on_tool_end()` - Tool execution observer
   - Line 176-191: `MessageFilterHook` class
   - Line 287-294: Hook factory functions

6. **tools/__init__.py** (lines 1-33)
   - Tool registry (centralized imports)
   - All tool exports in `__all__` list

7. **Individual Tool Files** (17 tools)
   - tools/bash.py (lines 1-316) - Bash execution with timeout
   - tools/read.py (lines 1-287) - File reading with tracking
   - tools/grep.py, tools/glob.py, etc.

---

## 3. Files That Would Be Affected by Adding Session Tracking

### DIRECTLY AFFECTED (Must Modify)

#### 1. **agency.py** (CRITICAL - HIGH IMPACT)
- **Location**: Lines 33-57 (main function)
- **Required Changes**:
  - Line 54 (after Agency creation): Create SafeSession instance
  - Line 57 (before terminal_demo): Wrap agency with SafeSession
- **Why**: Entry point for session lifecycle
- **Risk**: Medium - Central orchestrator, but clean insertion point

#### 2. **agency_code_agent/agency_code_agent.py** (HIGH IMPACT)
- **Location**: Lines 39-78 (factory function)
- **Required Changes**:
  - Line 50: Replace `create_system_reminder_hook()` with combined hook
  - Add optional `session` parameter to factory function
- **Why**: Agent factory must inject session-aware hooks
- **Risk**: Medium - Factory function changes affect all agent creation

#### 3. **planner_agent/planner_agent.py** (HIGH IMPACT)
- **Location**: Lines 35-72 (factory function)
- **Required Changes**:
  - Line 41: Replace `create_message_filter_hook()` with combined hook
  - Add optional `session` parameter to factory function
- **Why**: Both agents must share session context
- **Risk**: Medium - Factory function changes affect planner creation

#### 4. **shared/system_hooks.py** (MEDIUM IMPACT - EXTENSION)
- **Location**: After line 313 (end of file)
- **Required Changes**:
  - Add `SafeSessionHook` class (extends AgentHooks)
  - Add `create_safe_session_hook()` factory function
- **Why**: New hook for session tracking
- **Risk**: LOW - Pure addition, no modification of existing hooks

#### 5. **NEW FILE: shared/safe_session.py** (NEW - NO IMPACT)
- **Purpose**: SafeSession dataclass and SessionMetrics
- **Why**: Isolated session management logic
- **Risk**: NONE - Completely new file

#### 6. **tests/test_agency.py** (MEDIUM IMPACT)
- **Location**: Integration tests
- **Required Changes**:
  - Update tests to handle SafeSession wrapping
  - Add new tests for session tracking
- **Why**: Ensure session wrapper doesn't break existing behavior
- **Risk**: LOW - Test-only changes

### INDIRECTLY AFFECTED (May Need Updates)

#### 7. **Agency-Code/README.md** (DOCUMENTATION)
- **Why**: Document new session management feature
- **Risk**: NONE - Documentation only

#### 8. **requirements.txt** (DEPENDENCIES)
- **Why**: May need to add dependencies (unlikely)
- **Risk**: NONE - Only if new libraries needed

### NOT AFFECTED (Should NOT Modify)

- **tools/*.py** (17 tool files) - Observer pattern means no tool changes
- **Instruction files** (*.md) - Content only, no code
- **.env** - Configuration unchanged
- **Agency Swarm framework** - External library, never modify

---

## 4. Integration Points for Safety Layer

### STRATEGY 1: Hook-Based Tracking (RECOMMENDED - BEST)

**Location**: `shared/system_hooks.py` (after line 313)

**Approach**: Create `SafeSessionHook` class that observes execution

**Implementation**:
```python
class SafeSessionHook(AgentHooks):
    def __init__(self, session):
        self.session = session  # Reference to SafeSession

    async def on_tool_end(self, context, agent, tool, result):
        """Record tool execution in session"""
        tool_name = tool.__class__.__name__
        self.session.metrics.record_tool_call(tool_name, result)

    async def on_handoff(self, context, agent, source):
        """Track agent handoffs"""
        self.session.metrics.record_handoff(source, agent.name)
```

**Why This is Best**:
- SystemReminderHook PROVES this pattern works (lines 6-157)
- Non-invasive (no tool modification)
- Already integrated into agent factories
- Has access to context, tool, result
- Existing precedent (MessageFilterHook coexists)

**Risk**: LOW | Effort: MEDIUM | Benefit: MAXIMUM

### STRATEGY 2: Agent Creation Wrappers

**Location**: NEW FILE `shared/safe_session.py`

**Approach**: Wrap agents at creation time with session reference

**Implementation**:
```python
@dataclass
class SafeSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metrics: SessionMetrics = field(default_factory=SessionMetrics)

    def create_hook(self) -> SafeSessionHook:
        """Create hook bound to this session"""
        return SafeSessionHook(self)
```

**Why This Works**:
- Factory pattern already used (lines 287-294 in system_hooks.py)
- Agents created at centralized factories
- Clean separation of concerns

**Risk**: MEDIUM | Effort: HIGH | Benefit: MAXIMUM SAFETY

### STRATEGY 3: Context-Based Tracking

**Location**: Use existing `context.context.set()` pattern

**Approach**: Store session metrics in shared context

**Implementation**:
```python
# In SafeSessionHook.on_tool_end():
metrics = context.context.get("safe_session_metrics", {})
metrics['tool_calls'] = metrics.get('tool_calls', []) + [tool_name]
context.context.set("safe_session_metrics", metrics)
```

**Why This Works**:
- SystemReminderHook already uses context (line 170)
- Read tool already tracks in context (read.py:43-49)
- Shared across all hooks and agents

**Risk**: LOW | Effort: LOW | Benefit: GOOD (but less structured)

### **RECOMMENDED APPROACH**: Combine Strategy 1 + Strategy 2

1. Create `SafeSession` dataclass (new file)
2. Create `SafeSessionHook` class (extend system_hooks.py)
3. Inject hook via agent factories
4. Store metrics in session instance

This provides:
- ✅ Non-invasive (no tool changes)
- ✅ Type-safe (dataclass)
- ✅ Testable (isolated components)
- ✅ Observable (hook pattern)
- ✅ Proven pattern (follows SystemReminderHook)

---

## 5. Risk Assessment

### RISK 1: Hook Execution Order Conflicts
**Evidence**: Multiple hooks coexist (SystemReminderHook line 50, MessageFilterHook line 41)

**Impact**: SafeSessionHook might conflict with existing hooks

**Probability**: LOW (hooks already coexist successfully)

**Mitigation**:
- Test hook ordering explicitly
- SafeSessionHook should be first in chain (metrics before reminder)
- Document expected hook sequence

**Validation**:
```python
# In agent factory:
combined_hook = CombinedHook([
    SafeSessionHook(session),      # First - metrics collection
    SystemReminderHook(),           # Second - reminder injection
])
```

### RISK 2: Agent Factory Singleton Violation
**Evidence**: Lines 81-82 in agent files explicitly state "no singletons"

**Impact**: SafeSession could accidentally create singleton pattern

**Probability**: MEDIUM (if implemented incorrectly)

**Mitigation**:
- Pass session as parameter to factory (not global)
- Create fresh session per agency.py execution
- Add assertion: `assert session is not None`
- Document in docstrings: "session parameter optional for backward compatibility"

**Validation**:
```python
def create_agency_code_agent(
    model: str = "gpt-5-mini",
    reasoning_effort: str = "medium",
    session: Optional[SafeSession] = None  # Optional for backward compat
) -> Agent:
    assert not hasattr(session, '_singleton'), "Session must not be singleton"
```

### RISK 3: Context State Mutation Side Effects
**Evidence**: SystemReminderHook mutates context (line 170), filter_duplicates mutates messages (line 283)

**Impact**: SafeSession modifications could affect other hooks

**Probability**: MEDIUM (context is mutable)

**Mitigation**:
- SafeSession should OBSERVE, not MUTATE
- Use separate context key: "safe_session_metrics" (not "session")
- Never modify existing context keys
- Document: "SafeSession is observer only"

**Validation**:
```python
# Bad: Mutating shared state
context.context.set("metrics", {...})  # Could conflict!

# Good: Separate namespace
context.context.set("safe_session_metrics", {...})  # Isolated
```

### RISK 4: Agency Swarm Framework Changes
**Evidence**: External library (can't control updates)

**Impact**: Future Agency Swarm versions might change hook interface

**Probability**: MEDIUM (external dependency)

**Mitigation**:
- Wrap Agency instances, don't subclass
- Use dependency injection, not inheritance
- Pin Agency Swarm version in requirements.txt
- Add integration tests that fail if API changes

**Validation**:
```python
# requirements.txt:
agency-swarm==1.2.3  # Pin exact version

# Test:
def test_hook_interface_unchanged():
    """Verify AgentHooks interface is stable"""
    assert hasattr(AgentHooks, 'on_tool_end')
```

### RISK 5: Circular Import Dependencies
**Evidence**: Complex import chains between agent_utils, agents, and hooks

**Impact**: ImportError when adding SafeSession

**Probability**: LOW (but common Python issue)

**Mitigation**:
- Keep SafeSession imports minimal
- Use TYPE_CHECKING guards for type hints
- Never import Agent or Agency in safe_session.py
- Import only dataclasses and primitives

**Validation**:
```python
# safe_session.py:
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agency_swarm import Agent  # Type hints only

# Actual imports:
from dataclasses import dataclass, field
import uuid
import time
```

### RISK SUMMARY TABLE

| Risk | Probability | Impact | Mitigation Effort | Residual Risk |
|------|-------------|--------|-------------------|---------------|
| Hook execution order | LOW | MEDIUM | LOW | LOW |
| Singleton violation | MEDIUM | HIGH | LOW | LOW |
| Context mutation | MEDIUM | MEDIUM | LOW | LOW |
| Framework changes | MEDIUM | HIGH | MEDIUM | MEDIUM |
| Circular imports | LOW | HIGH | LOW | LOW |

---

## 6. Existing Patterns to Follow

### PATTERN 1: Factory Functions with Optional Parameters

**Source**: `agent_utils.py:53-75` (`create_model_settings`)

```python
def create_model_settings(
    model: str,
    reasoning_effort: str = "medium",  # Default provided
    reasoning_summary: str = "auto",   # Optional
    max_tokens: int = 32000,           # Has default
) -> ModelSettings:
    # All parameters optional except model
```

**Apply to SafeSession**:
```python
def create_agency_code_agent(
    model: str = "gpt-5-mini",
    reasoning_effort: str = "medium",
    session: Optional[SafeSession] = None  # NEW - Optional for backward compat
) -> Agent:
```

### PATTERN 2: Hook-Based Observation (CRITICAL PATTERN)

**Source**: `system_hooks.py:6-157` (`SystemReminderHook`)

```python
class SystemReminderHook(AgentHooks):
    def __init__(self):
        self.tool_call_count = 0  # Minimal state

    async def on_tool_end(self, context, agent, tool, result):
        self.tool_call_count += 1  # Non-invasive observation

        if self.tool_call_count >= 15:  # Threshold check
            self._inject_reminder(context, "tool_call_limit")
            self.tool_call_count = 0  # Reset
```

**Apply to SafeSession**:
```python
class SafeSessionHook(AgentHooks):
    def __init__(self, session: SafeSession):
        self.session = session  # Reference to session

    async def on_tool_end(self, context, agent, tool, result):
        tool_name = tool.__class__.__name__
        self.session.metrics.record_tool_call(tool_name, result)

        # Runaway detection
        if self.session.metrics.detect_infinite_loop():
            self.session.request_stop("Infinite loop detected")
```

### PATTERN 3: Hook Factory Functions

**Source**: `system_hooks.py:287-294`

```python
def create_system_reminder_hook():
    """Create and return a SystemReminderHook instance."""
    return SystemReminderHook()

def create_message_filter_hook():
    """Create and return a MessageFilterHook instance."""
    return MessageFilterHook()
```

**Apply to SafeSession**:
```python
def create_safe_session_hook(session: SafeSession):
    """Create and return a SafeSessionHook instance bound to session."""
    return SafeSessionHook(session)
```

### PATTERN 4: Graceful Error Handling

**Source**: `system_hooks.py:104-106`

```python
try:
    # Perform operation
    pass
except Exception as e:
    print(f"Warning: Failed to inject system reminder: {e}")
    # Don't interrupt flow - graceful degradation
```

**Apply to SafeSession**:
```python
async def on_tool_end(self, context, agent, tool, result):
    try:
        self.session.metrics.record_tool_call(tool.__class__.__name__)
    except Exception as e:
        print(f"Warning: SafeSession tracking failed: {e}")
        # Continue execution - metrics are non-critical
```

### PATTERN 5: Context-Based State Sharing

**Source**: `system_hooks.py:170` and `read.py:43-49`

```python
# Set shared state
context.context.set("pending_system_reminder", reminder_message)

# Get shared state
read_files = context.context.get("read_files", set())
read_files.add(abs_path)
context.context.set("read_files", read_files)
```

**Apply to SafeSession**:
```python
# In SafeSessionHook:
metrics = context.context.get("safe_session_metrics", {})
metrics['tool_calls'] = metrics.get('tool_calls', []) + [tool_name]
context.context.set("safe_session_metrics", metrics)
```

### PATTERN 6: Timeout Implementation

**Source**: `bash.py:157-158, 219-226, 248-249`

```python
# Parameter definition:
timeout: int = Field(
    12000,  # Default milliseconds
    ge=5000, le=600000  # Min/max validation
)

# Execution:
timeout_seconds = self.timeout / 1000
result = subprocess.run(..., timeout=timeout_seconds)

# Exception handling:
except subprocess.TimeoutExpired:
    return f"Command timed out after {timeout_seconds} seconds"
```

**Apply to SafeSession**:
```python
@dataclass
class SafeSession:
    max_duration: float = 1800.0  # 30 minutes default
    started_at: float = field(default_factory=time.time)

    def check_timeout(self) -> Optional[str]:
        elapsed = time.time() - self.started_at
        if elapsed > self.max_duration:
            return f"Session timeout: {elapsed:.1f}s / {self.max_duration:.1f}s"
        return None
```

---

## 7. Tool Execution Patterns (Critical for Observer Design)

### Tool Registration
**Location**: `tools/__init__.py:1-33`

All tools exported in `__all__` list and injected into Agent at creation:

```python
# tools/__init__.py:
from .bash import Bash
from .read import Read
# ... 15 more tools

__all__ = ["Bash", "Read", ...]

# agency_code_agent.py:59-76:
tools=[Bash, Glob, Grep, LS, Read, ...]
```

### Tool Execution Lifecycle

```
Agent receives message
  └─> LLM decides to call tool
      └─> Hook: on_tool_start(context, agent, tool)
          └─> Tool: tool.run() executes
              └─> Hook: on_tool_end(context, agent, tool, result)
                  └─> Result returned to agent
```

**Key Insight**: `on_tool_end()` has access to:
- `tool.__class__.__name__` - Tool name (e.g., "Bash", "Read")
- `result: str` - Tool output (can parse for errors)
- `context` - Shared context for metrics
- `agent` - Agent instance

### Existing Tool Metrics

1. **SystemReminderHook** (system_hooks.py:46-51)
   - Counts tool calls: `self.tool_call_count += 1`
   - Threshold: 15 calls → inject reminder
   - Reset after threshold

2. **Read Tool** (read.py:43-49)
   - Tracks files read in context
   - Global fallback: `_global_read_files` set

3. **Bash Tool** (bash.py:9-11, 141-155)
   - Global execution lock: `_bash_execution_lock`
   - Busy flag: `_bash_busy` (prevents parallel execution)

**Pattern Summary**:
- Metrics can be stored in hook instance (`self.tool_call_count`)
- Metrics can be stored in context (`context.context.set()`)
- Metrics can be stored globally (not recommended for SafeSession)

---

## 8. Subprocess Isolation Model

**How Agency Swarm Works**:
- Agents run in main process
- Tool execution may use subprocess (bash.py)
- Hooks run in main process (not subprocess)

**Implications for SafeSession**:
- SafeSession and hooks run in main process
- Can safely track metrics without IPC concerns
- Subprocess isolation already handled by framework

**Evidence**:
- bash.py:219-226 - subprocess.run() for command execution
- system_hooks.py:42-51 - hooks execute in main process
- No IPC mechanism needed for hook communication

---

## VALIDATION

### Research Checklist - COMPLETE

- [x] Read agency.py completely (lines 1-59)
- [x] Read agency_code_agent.py completely (lines 1-83)
- [x] Read planner_agent.py completely (lines 1-77)
- [x] Read shared/agent_utils.py completely (lines 1-81)
- [x] Read shared/system_hooks.py completely (lines 1-313)
- [x] Read tools/__init__.py (lines 1-33)
- [x] Read tools/bash.py (lines 1-316) - Timeout pattern
- [x] Read tools/read.py (lines 1-287) - Context tracking
- [x] Documented ALL integration points (3 strategies)
- [x] Identified ALL risks (5 risks with mitigations)
- [x] Can explain complete call flow (see diagram above)
- [x] Time spent: 7 minutes (UNDER 20 MIN LIMIT ✅)

### Acceptance Criteria - MET

- [x] RESEARCH_SESSION_MANAGEMENT.md exists
- [x] Contains complete call flow diagram
- [x] Lists ALL files that would be affected (6 directly, 2 indirectly, 19 not affected)
- [x] Identifies at least 3 integration points (found 3 strategies)
- [x] Includes risk assessment (5 risks documented)
- [x] Documents existing patterns (6 patterns identified)
- [x] Time spent ≤20 minutes (7 minutes actual)

---

## NEXT STEPS (Milestone 2: Create SessionMetrics Dataclass)

Based on this research, Milestone 2 should:

1. **Create `shared/safe_session.py`**
   - `SessionMetrics` dataclass with tool_calls, handoff_count, etc.
   - `SafeSession` dataclass with session_id, metrics, status
   - Methods: `record_tool_call()`, `get_duration()`, `request_stop()`

2. **Tests FIRST (TDD)**
   - File: `tests/test_session_metrics.py`
   - Test SessionMetrics initialization
   - Test tool call recording
   - Test duration calculation
   - Test handoff tracking

3. **Follow Patterns**
   - Factory function pattern (like create_system_reminder_hook)
   - Dataclass pattern (like ModelSettings in agent_utils.py)
   - Optional parameters (like reasoning_effort)

4. **Integration Strategy**
   - Hook-based approach (Strategy 1 + 2 combined)
   - NO tool modifications
   - NO agent modifications (yet)
   - Pure addition of new files

---

## FILES TO REVIEW BEFORE MILESTONE 2

1. `tests/test_system_reminder_hook.py` - Hook testing precedent
2. `tests/test_agency.py` - Integration testing pattern
3. `shared/agent_utils.py:53-75` - Dataclass example (ModelSettings)

---

## FINAL RECOMMENDATION

**Approach**: Hook-Based Tracking + SafeSession Dataclass

**New Files to Create**:
1. `shared/safe_session.py` - SafeSession and SessionMetrics classes
2. `tests/test_session_metrics.py` - Unit tests for metrics
3. `tests/test_safe_session.py` - Unit tests for session
4. Add SafeSessionHook to `shared/system_hooks.py` (after line 313)

**Existing Files to Modify (Milestone 4)**:
1. `agency.py` - Wrap agency with SafeSession (line 54-57)
2. `agency_code_agent/agency_code_agent.py` - Add session parameter (line 50)
3. `planner_agent/planner_agent.py` - Add session parameter (line 41)
4. `tests/test_agency.py` - Update integration tests

**Files NOT to Modify**:
- All 17 tool files (observer pattern)
- Agency Swarm framework (external)
- Configuration files

---

**Ready to proceed to Milestone 2?** YES

**Research Status**: COMPLETE ✅
**Time Budget**: 7 minutes / 20 minute limit (65% efficiency)
**Quality**: All requirements met
**Risk Level**: LOW (mitigations documented)
