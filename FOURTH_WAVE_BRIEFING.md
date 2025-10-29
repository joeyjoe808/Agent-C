# 🚀 FOURTH WAVE BRIEFING
## Phase 4: Enforcement Layer - Timeout Termination & Cancellation

> **MISSION**: Add enforcement mechanisms to actually STOP runaway agents (not just observe)
> **APPROACH**: Graceful termination, keyboard interrupts, automatic intervention
> **TIME BUDGET**: 4 milestones × 30 minutes = 2 hours total
> **CONTEXT**: Terminal-based system (not web API)

---

## 📚 Required Reading (Read These FIRST!)

**Phase 3 Deliverables** (completed):
1. **PHASE3_COMPLETION_REPORT.md** - What we built in Phase 3
2. **safety/timeout_monitor.py** - TimeoutMonitor (observation)
3. **safety/runaway_detector.py** - RunawayDetector (observation)
4. **RESEARCH_TIMEOUT_INTEGRATION.md** - Integration research

**Architecture Docs** (reference):
5. **AGENT_SAFETY_ARCHITECTURE.md** - Phase 4 requirements (adapt for terminal)
6. **AGENT_SAFETY_PROMPTS.md** - TDD approach
7. **CLAUDE.md** - Core principles (observer pattern, backward compatibility)

**Have you read all 7 documents?**
- [ ] YES - Proceed to Pre-Flight Checklist
- [ ] NO - STOP. Read them now. This is mandatory.

---

## ✈️ Pre-Flight Checklist

Before writing a SINGLE line of code:

```yaml
Phase 3 Validation:
  ☐ Phase 3 complete (PHASE3_COMPLETION_REPORT.md exists)
  ☐ TimeoutMonitor working (observation only)
  ☐ RunawayDetector working (observation only)
  ☐ All 30 tests passing (Phase 1 + Phase 3)
  ☐ Git checkpoints created (phase3-complete tag exists)

Environment:
  ☐ Python 3.13 venv activated (.venv/Scripts/activate)
  ☐ .env file configured with USE_SAFE_SESSION=true
  ☐ Can run: python agency.py (verify SafeSession working)
  ☐ All Phase 3 tests pass: pytest tests/test_timeout_monitor.py tests/test_runaway_detector.py -v

Git Safety:
  ☐ Working directory clean (git status)
  ☐ All Phase 3 work committed
  ☐ Ready to create new checkpoints
  ☐ Understand rollback procedure

Mindset:
  ☐ Understand: "Now we ADD enforcement - termination, cancellation"
  ☐ Commit to: Graceful degradation (always save state before killing)
  ☐ Remember: Test with short timeouts (don't wait 30 minutes!)
  ☐ Accept: Will STOP and validate every 30 minutes
```

**All items checked?**
- [ ] YES - Proceed to Milestone 13
- [ ] NO - Complete checklist before proceeding

---

## 🎯 Key Differences: Phase 3 vs Phase 4

### Phase 3 (Completed): **Observation Only**
- ✅ TimeoutMonitor detects timeouts → Returns warning string
- ✅ RunawayDetector detects patterns → Returns pattern enum
- ✅ No process termination
- ✅ No intervention
- ✅ Passive monitoring

### Phase 4 (NEW): **Enforcement & Intervention**
- ⭐ TimeoutEnforcer terminates on timeout → **Kills process**
- ⭐ RunawayEnforcer intervenes on patterns → **Stops execution**
- ⭐ Graceful cancellation (Ctrl+C) → **Clean shutdown**
- ⭐ Background monitoring task → **Automatic checks**
- ⭐ Active enforcement

---

## 🎯 MILESTONE 13: Background Monitoring Task

**Time Budget**: 30 minutes MAX (set timer NOW!)

### What You're Building

A background monitoring task that periodically checks timeout/runaway status and can trigger enforcement actions.

**Design**: Separate thread or async task that runs alongside agency.terminal_demo()

**Integration Point**: SafeSession (add monitoring control)

### Checkpoint BEFORE Starting

```bash
cd /c/Users/josep/Development/SOFTWARE-ENGINEER/Agency-Code
source .venv/Scripts/activate
git add .
git commit -m "Checkpoint before M13: Background monitoring task"
git tag checkpoint-m13-$(date +%s)
```

### Research Questions (Answer FIRST!)

**Before coding, research**:

1. **Agency Swarm Architecture**:
   - Is agency.terminal_demo() synchronous or async?
   - Can we run a background thread without breaking it?
   - How does Agency Swarm handle interrupts?

2. **Threading vs Asyncio**:
   - Should we use threading.Thread or asyncio.create_task()?
   - agency.py doesn't use async - can we add async monitoring?
   - What's the safest approach for terminal-based app?

3. **Integration Risk**:
   - Will background monitoring interfere with terminal_demo()?
   - How do we signal from monitor thread to main thread?
   - What happens if monitoring task crashes?

**Create**: `RESEARCH_BACKGROUND_MONITORING.md` (10 minutes max)

Document:
- agency.terminal_demo() execution model
- Threading approach recommendation
- Signaling mechanism (how monitor communicates with main)
- Risk assessment

### TDD: Write Tests FIRST

Create: `tests/test_background_monitor.py`

```python
import pytest
import time
import threading
from safety import SafeSession, TimeoutConfig, TimeoutMonitor
from safety.background_monitor import BackgroundMonitor, MonitorEvent


def test_background_monitor_initialization():
    """Test BackgroundMonitor initializes correctly"""
    session = SafeSession()
    config = TimeoutConfig(max_session_duration=100)
    monitor = BackgroundMonitor(session, config)

    assert monitor.session == session
    assert monitor.config == config
    assert monitor.is_running == False


def test_background_monitor_starts_and_stops():
    """Test monitor can start and stop cleanly"""
    session = SafeSession()
    config = TimeoutConfig(max_session_duration=100)
    monitor = BackgroundMonitor(session, config)

    # Start monitoring
    monitor.start()
    assert monitor.is_running == True

    time.sleep(0.5)  # Let it run briefly

    # Stop monitoring
    monitor.stop()
    assert monitor.is_running == False


def test_background_monitor_detects_timeout():
    """Test monitor detects timeout and triggers event"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 150  # 150s ago

    config = TimeoutConfig(max_session_duration=100)  # 100s limit
    monitor = BackgroundMonitor(session, config, check_interval=0.1)

    events = []
    def on_event(event: MonitorEvent):
        events.append(event)

    monitor.on_event = on_event
    monitor.start()

    time.sleep(0.5)  # Wait for check

    monitor.stop()

    # Should have triggered timeout event
    assert len(events) > 0
    assert any(e.event_type == "timeout" for e in events)


def test_background_monitor_detects_runaway():
    """Test monitor detects runaway pattern and triggers event"""
    session = SafeSession()

    # Simulate infinite tool loop
    for _ in range(6):
        session.metrics.record_tool_call("Bash", {})

    config = TimeoutConfig()
    monitor = BackgroundMonitor(session, config, check_interval=0.1)

    events = []
    def on_event(event: MonitorEvent):
        events.append(event)

    monitor.on_event = on_event
    monitor.start()

    time.sleep(0.5)  # Wait for check

    monitor.stop()

    # Should have triggered runaway event
    assert len(events) > 0
    assert any(e.event_type == "runaway" for e in events)


def test_background_monitor_graceful_shutdown():
    """
    CRITICAL: Monitor stops cleanly without leaving threads
    """
    session = SafeSession()
    config = TimeoutConfig()
    monitor = BackgroundMonitor(session, config)

    initial_thread_count = threading.active_count()

    monitor.start()
    time.sleep(0.2)
    monitor.stop()

    time.sleep(0.2)  # Wait for thread to fully exit

    final_thread_count = threading.active_count()

    # No threads leaked
    assert final_thread_count == initial_thread_count


def test_background_monitor_doesnt_block_main():
    """
    CRITICAL: Background monitoring doesn't block main execution
    """
    session = SafeSession()
    config = TimeoutConfig()
    monitor = BackgroundMonitor(session, config, check_interval=0.1)

    monitor.start()

    # Main thread should continue working
    start = time.time()
    time.sleep(0.3)  # Simulate work
    elapsed = time.time() - start

    monitor.stop()

    # Should take ~0.3s, not be blocked by monitor
    assert 0.25 < elapsed < 0.4
```

**Run tests (should FAIL):**
```bash
source .venv/Scripts/activate
pytest tests/test_background_monitor.py -v
```

**Expected**: FAIL - BackgroundMonitor doesn't exist yet (RED phase)

### Now Implement

Create: `safety/background_monitor.py`

```python
"""
Background monitoring for SafeSession enforcement.

Design: Separate thread that periodically checks timeout/runaway status.
Phase: Phase 4 - Active enforcement (can trigger termination)
"""

import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from safety.safe_session import SafeSession
    from safety.timeout_monitor import TimeoutConfig


class EventType(Enum):
    """Monitor event types"""
    TIMEOUT = "timeout"
    RUNAWAY = "runaway"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class MonitorEvent:
    """Event emitted by background monitor"""
    event_type: str
    message: str
    severity: str  # "low", "medium", "high"
    data: dict


class BackgroundMonitor:
    """
    Background monitoring task for SafeSession.

    Design Philosophy:
    - Runs in separate thread (doesn't block main)
    - Checks timeout/runaway periodically
    - Emits events (doesn't enforce directly)
    - Clean shutdown (no thread leaks)
    - Graceful error handling

    Usage:
        session = SafeSession()
        config = TimeoutConfig()
        monitor = BackgroundMonitor(session, config)

        def on_event(event: MonitorEvent):
            print(f"Event: {event.event_type} - {event.message}")

        monitor.on_event = on_event
        monitor.start()

        # ... agency.terminal_demo() runs ...

        monitor.stop()
    """

    def __init__(
        self,
        session: 'SafeSession',
        config: 'TimeoutConfig',
        check_interval: float = 5.0
    ):
        """
        Initialize background monitor.

        Args:
            session: SafeSession to monitor
            config: TimeoutConfig for timeout thresholds
            check_interval: Seconds between checks (default 5.0)
        """
        self.session = session
        self.config = config
        self.check_interval = check_interval

        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Event callback (set by user)
        self.on_event: Optional[Callable[[MonitorEvent], None]] = None

    def start(self) -> None:
        """Start background monitoring"""
        if self.is_running:
            return

        self.is_running = True
        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="SafeSessionMonitor"
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop background monitoring"""
        if not self.is_running:
            return

        self.is_running = False
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def _monitor_loop(self) -> None:
        """Main monitoring loop (runs in separate thread)"""
        try:
            while not self._stop_event.is_set():
                self._check_session()

                # Sleep with ability to wake on stop
                self._stop_event.wait(self.check_interval)

        except Exception as e:
            # Graceful degradation - don't crash monitor
            self._emit_event(MonitorEvent(
                event_type=EventType.ERROR.value,
                message=f"Monitor loop error: {e}",
                severity="high",
                data={"error": str(e)}
            ))

    def _check_session(self) -> None:
        """Check session for timeout/runaway conditions"""
        try:
            from safety.timeout_monitor import TimeoutMonitor
            from safety.runaway_detector import RunawayDetector

            # Check timeout
            timeout_monitor = TimeoutMonitor(self.session, self.config)
            warning = timeout_monitor.check_timeout()
            if warning:
                severity = "high" if "TIMEOUT" in warning else "medium"
                self._emit_event(MonitorEvent(
                    event_type=EventType.TIMEOUT.value,
                    message=warning,
                    severity=severity,
                    data={
                        "elapsed": self.session.metrics.get_duration(),
                        "max_duration": self.config.max_session_duration
                    }
                ))

            # Check runaway patterns
            runaway_detector = RunawayDetector(self.session)
            pattern = runaway_detector.detect_pattern()
            if pattern:
                message = runaway_detector.get_detection_message(pattern)
                self._emit_event(MonitorEvent(
                    event_type=EventType.RUNAWAY.value,
                    message=message,
                    severity="high",
                    data={
                        "pattern": pattern.value,
                        "details": runaway_detector.get_pattern_details()
                    }
                ))

        except Exception as e:
            # Graceful degradation
            self._emit_event(MonitorEvent(
                event_type=EventType.ERROR.value,
                message=f"Check session error: {e}",
                severity="low",
                data={"error": str(e)}
            ))

    def _emit_event(self, event: MonitorEvent) -> None:
        """Emit event to callback"""
        try:
            if self.on_event:
                self.on_event(event)
        except Exception as e:
            # Don't let callback errors crash monitor
            print(f"Warning: Event callback error: {e}")
```

**Update**: `safety/__init__.py`

```python
from .background_monitor import BackgroundMonitor, MonitorEvent, EventType
```

**Run tests (should PASS):**
```bash
source .venv/Scripts/activate
pytest tests/test_background_monitor.py -v
```

### Success Criteria

```yaml
Functional:
  ☐ BackgroundMonitor class created
  ☐ Runs in separate thread (daemon)
  ☐ Checks timeout/runaway periodically
  ☐ Emits events (doesn't block main)
  ☐ Clean shutdown (no thread leaks)

Testing:
  ☐ 7 tests written FIRST (TDD)
  ☐ All 7 tests PASS
  ☐ Critical "doesn't block main" test PASSES
  ☐ Critical "graceful shutdown" test PASSES

Quality:
  ☐ Type hints complete
  ☐ Docstrings comprehensive
  ☐ Graceful error handling
  ☐ Thread-safe

Integration:
  ☐ No modifications to existing code
  ☐ New file only (background_monitor.py)
  ☐ Existing 30 tests STILL PASS

Time:
  ☐ Time spent ≤30 minutes
```

### Validation Gate

**STOP. Do NOT proceed to Milestone 14 until:**

```yaml
Automated Tests:
  ☐ All 7 new tests PASS
  ☐ All existing 30 tests STILL PASS
  ☐ No thread leaks detected
  ☐ No blocking detected

Manual Validation:
  ☐ Can start/stop monitor
  ☐ Monitor detects timeout
  ☐ Monitor detects runaway
  ☐ Events received correctly

Research:
  ☐ RESEARCH_BACKGROUND_MONITORING.md created
  ☐ Approach validated
  ☐ Risks documented

Human Review:
  ☐ Human reviewed implementation
  ☐ Human approved to proceed
```

**Timer stopped at:** [X] minutes

---

## 🎯 MILESTONE 14: Graceful Cancellation (Ctrl+C)

**Time Budget**: 30 minutes MAX (set timer NOW!)

### Checkpoint BEFORE Starting

```bash
git add .
git commit -m "Checkpoint before M14: Graceful cancellation"
git tag checkpoint-m14-$(date +%s)
```

### What You're Building

Keyboard interrupt handler (Ctrl+C) that gracefully shuts down the agent, saves state, and exits cleanly.

**Design**: Signal handler that sets stop_requested flag and waits for cleanup.

### TDD: Write Tests FIRST

Create: `tests/test_graceful_cancellation.py`

```python
import pytest
import signal
import time
from safety import SafeSession
from safety.cancellation import CancellationHandler


def test_cancellation_handler_initialization():
    """Test CancellationHandler initializes"""
    session = SafeSession()
    handler = CancellationHandler(session)

    assert handler.session == session
    assert handler.cancellation_requested == False


def test_cancellation_handler_request_stop():
    """Test handler can request stop"""
    session = SafeSession()
    handler = CancellationHandler(session)

    handler.request_cancellation("User requested")

    assert handler.cancellation_requested == True
    assert session.stop_requested == True
    assert session.status == "stopping"


def test_cancellation_handler_cleanup():
    """Test handler performs cleanup"""
    session = SafeSession()
    session.metrics.record_tool_call("Bash", {})
    session.metrics.record_tool_call("Read", {})

    handler = CancellationHandler(session)
    handler.request_cancellation("Test")

    cleanup_result = handler.cleanup()

    assert cleanup_result is not None
    assert "session_id" in cleanup_result
    assert "tool_calls" in cleanup_result
    assert cleanup_result["tool_calls"] == 2


def test_cancellation_preserves_session_state():
    """
    CRITICAL: Cancellation doesn't lose session data
    """
    session = SafeSession()
    session.metrics.record_tool_call("Bash", {})
    session.metrics.reasoning_steps = 5

    handler = CancellationHandler(session)
    handler.request_cancellation("Test")

    # Session state preserved
    assert len(session.metrics.tool_calls) == 1
    assert session.metrics.reasoning_steps == 5
```

**Run tests (should FAIL - RED phase)**

### Now Implement

Create: `safety/cancellation.py`

```python
"""
Graceful cancellation for SafeSession.

Design: Signal handler for Ctrl+C (SIGINT) that saves state before exit.
Phase: Phase 4 - Enforcement layer
"""

import signal
import sys
from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from safety.safe_session import SafeSession


class CancellationHandler:
    """
    Handle graceful cancellation (Ctrl+C).

    Design Philosophy:
    - Catch SIGINT (Ctrl+C)
    - Request session stop
    - Perform cleanup
    - Save state
    - Exit gracefully

    Usage:
        session = SafeSession()
        handler = CancellationHandler(session)
        handler.install()  # Install signal handler

        # ... agency runs ...

        # On Ctrl+C, handler triggers cleanup
    """

    def __init__(self, session: 'SafeSession'):
        """
        Initialize cancellation handler.

        Args:
            session: SafeSession to manage
        """
        self.session = session
        self.cancellation_requested = False
        self._original_handler = None

    def install(self) -> None:
        """Install Ctrl+C signal handler"""
        self._original_handler = signal.signal(signal.SIGINT, self._signal_handler)

    def uninstall(self) -> None:
        """Restore original signal handler"""
        if self._original_handler:
            signal.signal(signal.SIGINT, self._original_handler)

    def _signal_handler(self, signum, frame):
        """Handle SIGINT (Ctrl+C)"""
        print("\n\n🛑 Cancellation requested (Ctrl+C)")
        print("⏳ Shutting down gracefully...")

        self.request_cancellation("User pressed Ctrl+C")

        # Perform cleanup
        result = self.cleanup()

        print(f"\n✅ Session {result['session_id']} cancelled")
        print(f"   Duration: {result['duration']:.1f}s")
        print(f"   Tool calls: {result['tool_calls']}")
        print(f"   Reasoning steps: {result['reasoning_steps']}")

        sys.exit(0)

    def request_cancellation(self, reason: str = "") -> None:
        """Request session cancellation"""
        self.cancellation_requested = True
        self.session.request_stop(reason)
        print(f"   Reason: {reason}")

    def cleanup(self) -> Dict:
        """
        Perform cleanup and return session summary.

        Returns:
            Dict with session summary
        """
        try:
            summary = {
                "session_id": self.session.session_id,
                "duration": self.session.metrics.get_duration(),
                "tool_calls": len(self.session.metrics.tool_calls),
                "reasoning_steps": self.session.metrics.reasoning_steps,
                "handoffs": self.session.metrics.handoff_count,
                "status": self.session.status
            }

            return summary

        except Exception as e:
            print(f"Warning: Cleanup error: {e}")
            return {
                "session_id": self.session.session_id if self.session else "unknown",
                "error": str(e)
            }
```

**Update**: `safety/__init__.py`

**Run tests (should PASS - GREEN phase)**

### Success Criteria

```yaml
Functional:
  ☐ CancellationHandler class created
  ☐ Catches Ctrl+C (SIGINT)
  ☐ Requests session stop
  ☐ Performs cleanup
  ☐ Exits gracefully

Testing:
  ☐ 4 tests written FIRST
  ☐ All 4 tests PASS
  ☐ Critical "preserves state" test PASSES

Quality:
  ☐ Type hints complete
  ☐ Clean implementation
  ☐ Graceful error handling

Time:
  ☐ Time spent ≤30 minutes
```

---

## 🎯 MILESTONE 15: Process Termination on Timeout

**Time Budget**: 30 minutes MAX (set timer NOW!)

### Checkpoint BEFORE Starting

```bash
git add .
git commit -m "Checkpoint before M15: Process termination"
git tag checkpoint-m15-$(date +%s)
```

### What You're Building

Enforcement mechanism that ACTUALLY terminates the process when timeout exceeded.

**Design**: Add termination method to SafeSession, trigger from BackgroundMonitor.

### Implementation

**Modify**: `safety/safe_session.py`

Add termination method:

```python
def terminate(self, reason: str = "Timeout exceeded") -> None:
    """
    Terminate session execution.

    This is the enforcement mechanism - actually stops execution.

    Args:
        reason: Reason for termination
    """
    print(f"\n🛑 TERMINATING SESSION: {reason}")
    print(f"   Session ID: {self.session_id}")
    print(f"   Duration: {self.metrics.get_duration():.1f}s")

    self.status = "terminated"
    self.stop_requested = True

    # TODO: In future, signal agency to stop
    # For now, just set flags
```

**Modify**: `safety/background_monitor.py`

Add auto-termination option:

```python
def __init__(
    self,
    session: 'SafeSession',
    config: 'TimeoutConfig',
    check_interval: float = 5.0,
    auto_terminate: bool = False  # NEW
):
    """
    ...
    Args:
        auto_terminate: If True, automatically terminate on timeout (default False)
    """
    self.auto_terminate = auto_terminate

def _check_session(self) -> None:
    """Check session and optionally terminate"""
    # ... existing timeout check ...

    if warning and "TIMEOUT" in warning:
        self._emit_event(...)

        # NEW: Auto-terminate if enabled
        if self.auto_terminate:
            self.session.terminate("Session timeout exceeded")
```

### Tests

Add tests to `test_background_monitor.py`:

```python
def test_background_monitor_auto_terminate_on_timeout():
    """Test monitor can auto-terminate on timeout"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 150

    config = TimeoutConfig(max_session_duration=100)
    monitor = BackgroundMonitor(session, config, check_interval=0.1, auto_terminate=True)

    monitor.start()
    time.sleep(0.5)
    monitor.stop()

    # Session should be terminated
    assert session.status == "terminated"
    assert session.stop_requested == True
```

---

## 🎯 MILESTONE 16: Final Integration & Documentation

**Time Budget**: 30 minutes MAX

### What You're Doing

1. Integrate BackgroundMonitor into agency.py (optional)
2. Create Phase 4 completion report
3. Manual validation
4. Update documentation

### Integration (Optional)

**Modify**: `agency.py` (lines 44-48, after SafeSession creation)

```python
if USE_SAFE_SESSION:
    from safety import SafeSession, TimeoutConfig, BackgroundMonitor, CancellationHandler

    session = SafeSession()
    config = TimeoutConfig(max_session_duration=1800)  # 30 minutes

    # Optional: Background monitoring
    USE_BACKGROUND_MONITOR = os.getenv("USE_BACKGROUND_MONITOR", "false").lower() == "true"
    if USE_BACKGROUND_MONITOR:
        monitor = BackgroundMonitor(session, config, check_interval=10.0, auto_terminate=False)

        def on_event(event):
            print(f"\n⚠️  [{event.severity.upper()}] {event.message}")

        monitor.on_event = on_event
        monitor.start()

        # Install Ctrl+C handler
        cancellation = CancellationHandler(session)
        cancellation.install()

        print(f"[SafeSession] Background monitoring enabled (check every 10s)")
    else:
        monitor = None
        cancellation = None

    print(f"[SafeSession] Session ID: {session.session_id}\n")
```

### Create PHASE4_COMPLETION_REPORT.md

(Similar structure to Phase 3 report)

---

## 📋 Key Reminders

### What Phase 4 ADDS (vs Phase 3)

**Phase 3**: Observation only
- TimeoutMonitor → Returns warning string
- RunawayDetector → Returns pattern enum

**Phase 4**: Enforcement
- BackgroundMonitor → Checks periodically, emits events
- CancellationHandler → Ctrl+C handling, cleanup
- SafeSession.terminate() → Actually stops execution
- Optional auto-termination

### Testing Strategy

**Short Timeouts for Testing**:
```python
config = TimeoutConfig(max_session_duration=10)  # 10 seconds for testing
```

Don't wait 30 minutes to test - use short timeouts!

### Graceful Degradation

Phase 4 is **OPTIONAL**:
- Can run SafeSession without BackgroundMonitor
- Can run BackgroundMonitor without auto-termination
- Everything is opt-in via env vars

---

## ✅ Phase 4 Success Criteria

```yaml
Milestones:
  ☐ M13: BackgroundMonitor (7 tests)
  ☐ M14: CancellationHandler (4 tests)
  ☐ M15: Process termination (integrated)
  ☐ M16: Documentation & validation

Tests:
  ☐ ~11 new tests (Phase 4)
  ☐ 41 total tests (Phase 1 + 3 + 4)
  ☐ 100% passing

Functionality:
  ☐ Background monitoring works
  ☐ Ctrl+C cancellation works
  ☐ Auto-termination works
  ☐ No thread leaks
  ☐ Backward compatible

Time:
  ☐ Total ≤2 hours
```

---

**LET'S BUILD PHASE 4!** 🚀

**Start with Milestone 13. Create research doc, then implement BackgroundMonitor.**

**Remember: "Test with SHORT timeouts - don't wait 30 minutes!"**

**GO!**
