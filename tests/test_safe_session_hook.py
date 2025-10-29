"""
Tests for SafeSessionHook - TDD Implementation

Following exact pattern from SystemReminderHook (system_hooks.py lines 6-157)

Critical Test: Coexistence with existing hooks (no conflicts)
"""

import pytest
import asyncio
from shared.system_hooks import SafeSessionHook
from safety.safe_session import SafeSession


def test_safe_session_hook_initialization():
    """Test SafeSessionHook initializes with session reference"""
    session = SafeSession()
    hook = SafeSessionHook(session)

    assert hook.session == session
    assert hook.session.session_id is not None


def test_safe_session_hook_records_tool_calls():
    """Test on_tool_end records tool calls to session"""
    session = SafeSession()
    hook = SafeSessionHook(session)

    # Mock tool
    class MockTool:
        pass
    MockTool.__name__ = "Bash"

    # Simulate tool end
    async def run_test():
        await hook.on_tool_end(None, None, MockTool(), "success")

    asyncio.run(run_test())

    assert len(session.metrics.tool_calls) == 1
    assert session.metrics.tool_calls[0][0] == "Bash"


def test_safe_session_hook_records_handoffs():
    """Test on_handoff records agent handoffs"""
    session = SafeSession()
    hook = SafeSessionHook(session)

    # Mock agent
    class MockAgent:
        name = "PlannerAgent"

    async def run_test():
        await hook.on_handoff(None, MockAgent(), "AgencyCodeAgent")

    asyncio.run(run_test())

    assert session.metrics.handoff_count == 1


def test_safe_session_hook_coexists_with_system_reminder():
    """CRITICAL: Prove SafeSessionHook doesn't conflict with existing hooks"""
    from shared.system_hooks import SystemReminderHook

    session = SafeSession()
    safe_hook = SafeSessionHook(session)
    reminder_hook = SystemReminderHook()

    # Both instantiable
    assert safe_hook is not None
    assert reminder_hook is not None

    # Mock tool
    class MockTool:
        pass
    MockTool.__name__ = "Bash"

    async def run_test():
        await safe_hook.on_tool_end(None, None, MockTool(), "success")
        await reminder_hook.on_tool_end(None, None, MockTool(), "success")

    asyncio.run(run_test())

    # SafeSessionHook recorded
    assert len(session.metrics.tool_calls) == 1

    # SystemReminderHook incremented
    assert reminder_hook.tool_call_count == 1
