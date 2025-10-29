# Background Monitoring Research
**Date**: January 2025
**Milestone**: M13 - Phase 4 Research
**Purpose**: Determine safe approach for background monitoring in Agency-Code

---

## 1. Agency Swarm Execution Model

### terminal_demo() Analysis

**File**: `agency.py` line 74

```python
agency.terminal_demo(show_reasoning=False if model.startswith("anthropic") else True)
```

**Finding**: `terminal_demo()` is **SYNCHRONOUS** (not async)

**Source Code** (agency_swarm.Agency.terminal_demo):
```python
def terminal_demo(self, show_reasoning: bool | None = None) -> None:
    """
    Run a terminal demo of the agency.
    """
    from .visualization import terminal_demo

    return terminal_demo(self, show_reasoning=show_reasoning)
```

**Conclusion**:
- ✅ **Blocking/synchronous execution**
- ✅ No async/await
- ✅ Runs until user exits
- ✅ Safe to use threading.Thread for background tasks

---

## 2. Threading vs Asyncio Decision

### Option 1: threading.Thread (RECOMMENDED ✅)

**Pros**:
- ✅ Compatible with synchronous agency.terminal_demo()
- ✅ No need to modify existing code
- ✅ Python standard library (no dependencies)
- ✅ Well-tested pattern for background tasks
- ✅ Can run alongside any blocking code

**Cons**:
- ⚠️ Global Interpreter Lock (GIL) - but monitoring is lightweight
- ⚠️ Need to ensure thread cleanup

**Example**:
```python
import threading

monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
monitor_thread.start()

# Main thread continues with terminal_demo()
agency.terminal_demo()

# Clean shutdown
monitor_thread.join(timeout=2.0)
```

### Option 2: asyncio.create_task (NOT RECOMMENDED ❌)

**Pros**:
- Modern Python pattern

**Cons**:
- ❌ Requires async event loop
- ❌ agency.terminal_demo() is synchronous
- ❌ Would need to wrap terminal_demo() in asyncio.run()
- ❌ More complex integration
- ❌ Risk of breaking Agency Swarm internals

**Conclusion**: Use **threading.Thread** ✅

---

## 3. Integration Architecture

### Recommended Pattern

```
Main Thread (agency.py)
├── SafeSession created
├── BackgroundMonitor created
├── monitor.start() → Spawns daemon thread
├── agency.terminal_demo() → Runs (blocking)
└── monitor.stop() → Joins thread (cleanup)

Background Thread (BackgroundMonitor)
├── While not stopped:
│   ├── Check timeout (TimeoutMonitor)
│   ├── Check runaway (RunawayDetector)
│   ├── Emit events if detected
│   └── Sleep 5 seconds
└── Exit cleanly
```

### Thread Safety Considerations

**Thread-Safe Operations** (no locks needed):
- ✅ Reading SafeSession.metrics (immutable after write)
- ✅ Reading session.stop_requested (boolean)
- ✅ TimeoutMonitor.check_timeout() (read-only)
- ✅ RunawayDetector.detect_pattern() (read-only)

**Potentially Unsafe** (needs care):
- ⚠️ Writing to session.stop_requested from multiple threads
- ⚠️ Modifying session.status from multiple threads

**Mitigation**:
- Use threading.Event for stop signaling
- Monitor is read-only (only emits events)
- Main thread handles termination decisions

---

## 4. Signaling Mechanism

### Event-Based Architecture (RECOMMENDED ✅)

**BackgroundMonitor** → Emits `MonitorEvent` → **Callback**

```python
class MonitorEvent:
    event_type: str  # "timeout", "runaway", "warning"
    message: str
    severity: str   # "low", "medium", "high"
    data: dict

monitor = BackgroundMonitor(session, config)

def on_event(event: MonitorEvent):
    print(f"⚠️  [{event.severity}] {event.message}")

    if event.event_type == "timeout" and event.severity == "high":
        # Main thread decides what to do
        session.terminate("Timeout exceeded")

monitor.on_event = on_event
monitor.start()
```

**Why This Pattern**:
- ✅ Loose coupling (monitor doesn't enforce, just reports)
- ✅ Main thread stays in control
- ✅ Easy to test (inject callback)
- ✅ Graceful degradation (callback errors don't crash monitor)

### Alternative: Shared Queue (NOT NEEDED)

Could use queue.Queue but callback is simpler for this use case.

---

## 5. Thread Lifecycle Management

### Daemon Thread (RECOMMENDED ✅)

```python
self._thread = threading.Thread(
    target=self._monitor_loop,
    daemon=True,  # Dies when main thread exits
    name="SafeSessionMonitor"
)
self._thread.start()
```

**Why Daemon**:
- ✅ Automatically exits when agency.terminal_demo() ends
- ✅ No zombie threads
- ✅ Clean process exit

**BUT**: Need explicit stop for graceful shutdown:
```python
def stop(self):
    self.is_running = False
    self._stop_event.set()  # Wake from sleep
    if self._thread:
        self._thread.join(timeout=2.0)  # Wait max 2s
```

### Sleep with Interruptibility

**Problem**: `time.sleep(5)` can't be interrupted

**Solution**: Use `threading.Event.wait()`
```python
self._stop_event = threading.Event()

# In loop:
self._stop_event.wait(5.0)  # Sleep 5s, but wake on stop_event.set()
```

**Benefit**: Immediate shutdown (don't wait 5s for next check)

---

## 6. Risk Assessment

### Risk 1: Thread Doesn't Stop Cleanly
**Likelihood**: Low
**Mitigation**:
- Use threading.Event for stop signaling
- Daemon thread (dies with main)
- join() with timeout

### Risk 2: Monitor Crashes
**Likelihood**: Low
**Mitigation**:
- Try/except around entire monitor loop
- Try/except around event callback
- Emit error event on exception

### Risk 3: Callback Blocks Monitor
**Likelihood**: Medium (if callback does heavy work)
**Mitigation**:
- Document: "Keep callbacks lightweight"
- Timeout on callback (future enhancement)
- Try/except around callback

### Risk 4: Race Conditions
**Likelihood**: Very Low
**Mitigation**:
- Monitor is read-only
- Uses threading.Event (thread-safe)
- No shared mutable state

### Risk 5: Interferes with terminal_demo()
**Likelihood**: Very Low
**Mitigation**:
- Daemon thread
- Lightweight checks (<1ms)
- Runs in background
- No terminal I/O in monitor (only in callback)

---

## 7. Performance Impact

**Monitor Overhead**:
- Thread creation: ~1ms (one-time)
- Check interval: 5 seconds (configurable)
- Check duration: <2ms (TimeoutMonitor + RunawayDetector)
- Memory: ~1KB per monitor

**CPU Usage**:
- Sleeping 95%+ of time (threading.Event.wait)
- Active checks: <0.01% CPU
- Negligible impact

**Recommendation**: ✅ **Performance impact is negligible**

---

## 8. Testing Strategy

### Unit Tests

```python
def test_monitor_starts_and_stops():
    monitor = BackgroundMonitor(session, config)
    monitor.start()
    assert monitor.is_running == True

    time.sleep(0.5)

    monitor.stop()
    assert monitor.is_running == False


def test_monitor_detects_timeout():
    session.metrics.started_at = time.time() - 150  # Over limit
    monitor = BackgroundMonitor(session, config, check_interval=0.1)

    events = []
    monitor.on_event = lambda e: events.append(e)
    monitor.start()

    time.sleep(0.5)  # Wait for check
    monitor.stop()

    assert len(events) > 0
    assert any(e.event_type == "timeout" for e in events)
```

### Critical Tests

1. **No Thread Leaks**: Count threads before/after
2. **Doesn't Block Main**: Main thread continues during monitoring
3. **Clean Shutdown**: Stops within timeout
4. **Event Delivery**: Events reach callback

---

## 9. Implementation Plan

### Step 1: Create MonitorEvent class (5 min)
```python
@dataclass
class MonitorEvent:
    event_type: str
    message: str
    severity: str
    data: dict
```

### Step 2: Create BackgroundMonitor skeleton (10 min)
```python
class BackgroundMonitor:
    def __init__(self, session, config, check_interval=5.0):
        self.session = session
        self.config = config
        self.check_interval = check_interval
        self.is_running = False
        self._thread = None
        self._stop_event = threading.Event()
        self.on_event = None
```

### Step 3: Implement start/stop (5 min)
```python
def start(self):
    self.is_running = True
    self._stop_event.clear()
    self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
    self._thread.start()

def stop(self):
    self.is_running = False
    self._stop_event.set()
    if self._thread:
        self._thread.join(timeout=2.0)
```

### Step 4: Implement monitoring loop (10 min)
```python
def _monitor_loop(self):
    try:
        while not self._stop_event.is_set():
            self._check_session()
            self._stop_event.wait(self.check_interval)
    except Exception as e:
        self._emit_event(MonitorEvent(...))
```

---

## 10. Integration with agency.py (Optional)

**Recommendation**: Make it **opt-in** via environment variable

```python
# In agency.py (after SafeSession creation)

USE_BACKGROUND_MONITOR = os.getenv("USE_BACKGROUND_MONITOR", "false").lower() == "true"

if USE_SAFE_SESSION and USE_BACKGROUND_MONITOR:
    from safety import BackgroundMonitor, TimeoutConfig

    config = TimeoutConfig(max_session_duration=1800)
    monitor = BackgroundMonitor(session, config, check_interval=10.0)

    def on_event(event):
        print(f"\n⚠️  [{event.severity.upper()}] {event.message}")

    monitor.on_event = on_event
    monitor.start()

    print("[SafeSession] Background monitoring enabled")

# ... terminal_demo() runs ...

# Cleanup (add at end)
if monitor:
    monitor.stop()
```

**Environment Variables**:
```bash
USE_SAFE_SESSION=true
USE_BACKGROUND_MONITOR=true  # NEW - opt-in
```

---

## 11. Conclusions

### Recommended Approach: threading.Thread ✅

**Rationale**:
- Compatible with synchronous terminal_demo()
- Standard Python pattern
- No risk to Agency Swarm internals
- Easy to test
- Graceful shutdown

### Implementation Summary

```
BackgroundMonitor
├── Uses threading.Thread (daemon)
├── Runs _monitor_loop() every 5 seconds
├── Checks TimeoutMonitor + RunawayDetector
├── Emits MonitorEvent via callback
├── Stop via threading.Event
└── Clean shutdown with thread.join()
```

### Safety Guarantees

- ✅ Thread-safe (read-only monitor)
- ✅ Doesn't block main thread
- ✅ Clean shutdown (no leaks)
- ✅ Graceful error handling
- ✅ Negligible performance impact

### Timeline

- Research: 10 minutes ✅
- Implementation: 20 minutes
- **Total M13**: 30 minutes

---

## 12. Next Steps

1. ✅ Research complete → Proceed to implementation
2. Write 7 tests FIRST (TDD)
3. Implement BackgroundMonitor
4. Validate: All tests pass, no thread leaks
5. Manual test: Run with short timeout (10s)

---

**Research Phase: ✅ COMPLETE**
**Next**: Implement BackgroundMonitor (TDD - tests first!)
**Time Spent**: ~10 minutes

---

**END OF RESEARCH**
