# BUG FIX: TypeError - Agent hooks must be an AgentHooks instance

## Problem

**Error Message:**
```
TypeError: Agent hooks must be an AgentHooks instance or None, got list
```

**Root Cause:**
In `agency_code_agent.py` and `planner_agent.py`, when a SafeSession was provided, the code attempted to pass multiple hooks as a list:

```python
hooks = [reminder_hook, safe_hook]  # INCORRECT - agency_swarm doesn't accept lists
```

Agency Swarm's Agent class only accepts:
- A single AgentHooks instance
- None
- NOT a list of hooks

**Location of Bug:**
- `agency_code_agent/agency_code_agent.py` (line 69)
- `planner_agent/planner_agent.py` (line 62)

---

## Solution

Created a `CombinedHook` wrapper class that combines multiple hooks into a single AgentHooks instance.

### Implementation

**1. Added CombinedHook class to `shared/system_hooks.py` (line 300-363)**

```python
class CombinedHook(AgentHooks):
    """
    Wrapper to combine multiple hooks into one.

    Allows multiple hooks to be used together by calling each hook's
    methods in sequence.
    """

    def __init__(self, hooks: list):
        """Initialize with list of hooks."""
        self.hooks = hooks

    async def on_start(self, context, agent):
        """Call on_start for all hooks."""
        for hook in self.hooks:
            if hasattr(hook, 'on_start'):
                await hook.on_start(context, agent)

    # ... similar methods for on_end, on_handoff, on_tool_start,
    # on_tool_end, on_llm_start, on_llm_end
```

**2. Updated `agency_code_agent/agency_code_agent.py` (lines 65-72)**

```python
# BEFORE (BROKEN):
if session is not None:
    from shared.system_hooks import create_safe_session_hook
    safe_hook = create_safe_session_hook(session)
    hooks = [reminder_hook, safe_hook]  # ❌ TypeError
else:
    hooks = reminder_hook

# AFTER (FIXED):
if session is not None:
    from shared.system_hooks import create_safe_session_hook, CombinedHook
    safe_hook = create_safe_session_hook(session)
    hooks = CombinedHook([reminder_hook, safe_hook])  # ✅ Single AgentHooks instance
else:
    hooks = reminder_hook
```

**3. Updated `planner_agent/planner_agent.py` (lines 57-65)**

```python
# BEFORE (BROKEN):
if session is not None:
    from shared.system_hooks import create_safe_session_hook
    safe_hook = create_safe_session_hook(session)
    hooks = [filter_hook, safe_hook]  # ❌ TypeError
else:
    hooks = filter_hook

# AFTER (FIXED):
if session is not None:
    from shared.system_hooks import create_safe_session_hook, CombinedHook
    safe_hook = create_safe_session_hook(session)
    hooks = CombinedHook([filter_hook, safe_hook])  # ✅ Single AgentHooks instance
else:
    hooks = filter_hook
```

---

## Validation

### Test Results

Created and ran `test_hook_fix.py` which verified:

1. **Single hook works** (backward compatible)
   - Type: SystemReminderHook
   - Is AgentHooks instance: True
   - ✓ PASS

2. **Multiple hooks with CombinedHook work**
   - Type: CombinedHook
   - Is AgentHooks instance: True
   - Contains 2 hooks
   - ✓ PASS

3. **Hooks is NOT a list** (bug fixed)
   - Type: CombinedHook (not list)
   - Is list: False
   - Is AgentHooks: True
   - ✓ PASS

4. **Agent factory logic works**
   - Without session: single hook (backward compatible)
   - With session: CombinedHook (fixed)
   - ✓ PASS

### Test Output

```
============================================================
Testing Hook Type Fix
============================================================

1. Testing single hook (backward compatible):
   Type: SystemReminderHook
   Is AgentHooks instance: True
   ✓ Single hook is valid AgentHooks instance

2. Testing multiple hooks with CombinedHook:
   Type: CombinedHook
   Is AgentHooks instance: True
   Contains 2 hooks
   ✓ CombinedHook is valid AgentHooks instance

3. Verifying hooks is NOT a list:
   Type of combined: <class 'shared.system_hooks.CombinedHook'>
   Is list: False
   Is AgentHooks: True
   ✓ hooks is NOT a list (TypeError fixed)

4. Simulating agent factory logic:
   Without session: hooks type = SystemReminderHook
   Is list: False
   ✓ Without session: single hook (backward compatible)
   With session: hooks type = CombinedHook
   Is list: False
   Contains 2 hooks
   ✓ With session: CombinedHook (fixed)

============================================================
✓ ALL TESTS PASSED - TypeError FIXED!
============================================================
```

---

## Files Modified

1. **`shared/system_hooks.py`**
   - Added CombinedHook class (lines 300-363)
   - Implements all AgentHooks methods (on_start, on_end, on_handoff, on_tool_start, on_tool_end, on_llm_start, on_llm_end)
   - Calls each hook's method in sequence

2. **`agency_code_agent/agency_code_agent.py`**
   - Line 66: Import CombinedHook
   - Line 69: Use CombinedHook([reminder_hook, safe_hook]) instead of list

3. **`planner_agent/planner_agent.py`**
   - Line 59: Import CombinedHook
   - Line 62: Use CombinedHook([filter_hook, safe_hook]) instead of list

---

## Design Pattern

The fix follows the **Composite Pattern**:
- CombinedHook acts as a composite that contains multiple hooks
- It implements the same AgentHooks interface
- Each method delegates to all contained hooks in sequence
- Agency Swarm sees a single AgentHooks instance (not a list)

**Benefits:**
- Transparent to Agency Swarm (single AgentHooks instance)
- Backward compatible (without session, uses single hook)
- Extensible (can add more hooks in the future)
- Clean separation of concerns (each hook has its own responsibility)

---

## Note on Full Agency Testing

Full end-to-end testing of `agency.py` is currently blocked by a Python 3.14 incompatibility:

```
ValueError: '3.14' is not a valid PythonVersion
```

This is a dependency issue with `datamodel-code-generator` which doesn't support Python 3.14 yet.

**The CombinedHook fix itself is confirmed working through:**
- Unit tests (test_hook_fix.py)
- Python syntax validation (py_compile)
- Type checking (verified AgentHooks methods)
- Logic simulation (verified agent factory behavior)

**To test full agency.py startup:**
- Use Python 3.13 or earlier
- Or wait for datamodel-code-generator to support Python 3.14

---

## Summary

**FIXED:** TypeError "Agent hooks must be an AgentHooks instance or None, got list"

**CHANGES:**
1. Added CombinedHook class to system_hooks.py
2. Updated agency_code_agent.py to use CombinedHook
3. Updated planner_agent.py to use CombinedHook

**VERIFIED:**
- All syntax checks pass
- Unit tests pass
- Logic simulation passes
- Backward compatibility maintained

**STATUS:** Ready for production (once Python 3.14 dependency issue resolved)
