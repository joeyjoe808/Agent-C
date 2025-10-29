"""
Integration tests for SafeSession with real Agency-Code agents.

CRITICAL: These tests prove SafeSession doesn't break existing functionality.

TDD RED PHASE: These tests validate SafeSession integration without modifying
any existing agent code. Test 1 is the MOST CRITICAL - it proves existing
agent creation still works unaffected.

Philosophy:
- PROVE existing agent creation unaffected
- PROVE SafeSession wraps without breaking
- PROVE metrics tracking works
- PROVE stop request mechanism works
"""

import pytest
import sys
import os

# Add Agency-Code to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safety.safe_session import SafeSession
from agency_code_agent.agency_code_agent import create_agency_code_agent
from planner_agent.planner_agent import create_planner_agent


def test_existing_agent_creation_unaffected():
    """
    CRITICAL TEST: Prove existing agent creation still works.

    This is THE MOST IMPORTANT test. If this fails, we broke something.

    This test MUST pass - it validates that our SafeSession implementation
    does NOT break the existing agent creation flow. All agent creation
    should work EXACTLY as before, with no changes to agent files.

    Philosophy: "PROVE existing functionality unaffected"
    """
    # Create agent normally (no SafeSession involvement)
    agent = create_agency_code_agent(model="claude-haiku-4-5-20251001")

    # Agent should work exactly as before
    assert agent is not None, "Agent creation should succeed"
    assert agent.name == "AgencyCodeAgent", "Agent should have correct name"

    # Verify agent has all expected attributes
    assert hasattr(agent, "name"), "Agent should have name attribute"
    assert hasattr(agent, "description"), "Agent should have description attribute"
    assert hasattr(agent, "instructions"), "Agent should have instructions attribute"
    assert hasattr(agent, "model"), "Agent should have model attribute"
    assert hasattr(agent, "tools"), "Agent should have tools attribute"

    # Verify agent description is correct
    assert "interactive CLI tool" in agent.description.lower(), \
        "Agent description should be correct"

    # Verify agent has tools
    assert len(agent.tools) > 0, "Agent should have tools configured"

    # Verify agent model is set
    assert agent.model is not None, "Agent model should be configured"

    # CRITICAL: Nothing about agent creation should have changed
    # This test proves we haven't broken existing functionality


def test_safe_session_wraps_real_agent():
    """
    Test SafeSession can wrap real agent without breaking it.

    This test proves the transparent wrapper pattern works correctly:
    - Agent creation works normally
    - SafeSession wraps without modifying agent
    - Wrapped agent retains all original properties
    - Session becomes active upon wrapping

    Philosophy: "Observer pattern - watch, don't modify"
    """
    # Create real agent using existing factory
    agent = create_agency_code_agent(model="claude-haiku-4-5-20251001")

    # Create SafeSession
    session = SafeSession()

    # Verify session starts in correct state
    assert session.status == "initializing", "New session should be initializing"
    assert session._agent is None, "Agent should not be set yet"
    assert session.is_active() is False, "Session should not be active yet"

    # Wrap agent with SafeSession
    session.set_agent(agent)

    # Verify session state after wrapping
    assert session._agent is agent, "Session should reference the agent"
    assert session._agent.name == "AgencyCodeAgent", "Wrapped agent should retain properties"
    assert session.status == "active", "Session should be active after setting agent"
    assert session.is_active() is True, "is_active() should return True"

    # Verify agent itself is unchanged
    assert agent.name == "AgencyCodeAgent", "Agent properties should be unchanged"
    assert hasattr(agent, "tools"), "Agent should still have all attributes"
    assert hasattr(agent, "model"), "Agent should still have model"

    # Verify session has unique ID
    assert session.session_id is not None, "Session should have unique ID"
    assert len(session.session_id) > 0, "Session ID should not be empty"

    # Verify metrics initialized
    assert session.metrics is not None, "Session should have metrics"

    # CRITICAL: Agent wrapper is transparent - agent works exactly as before


def test_safe_session_tracks_real_execution():
    """
    Test SafeSession tracks metrics during real execution.

    NOTE: This simulates tool calls, doesn't actually execute agent.
    We test the observation/tracking mechanism without making API calls.

    This test proves:
    - Tool call recording works
    - Metrics are accumulated correctly
    - Session duration tracking works
    - Multiple tool calls tracked independently

    Philosophy: "PROVE it works by testing"
    """
    # Create SafeSession with real agent
    session = SafeSession()
    agent = create_agency_code_agent(model="claude-haiku-4-5-20251001")
    session.set_agent(agent)

    # Verify initial state
    assert len(session.metrics.tool_calls) == 0, "Should start with no tool calls"
    assert session.metrics.total_tool_calls == 0, "Total tool calls should be zero"

    # Simulate tool calls (as would happen in real execution)
    session.record_tool_call("WebFetch", {"url": "test.com"})
    session.record_tool_call("FileRead", {"path": "/test.txt"})
    session.record_tool_call("Bash", {"command": "ls -la"})

    # Verify tracking works
    assert len(session.metrics.tool_calls) == 3, "Should track all 3 tool calls"
    assert session.metrics.total_tool_calls == 3, "Total count should be 3"

    # Verify tool call details
    first_call = session.metrics.tool_calls[0]
    assert first_call[0] == "WebFetch", "First tool should be WebFetch"
    assert first_call[1]["url"] == "test.com", "Tool args should be preserved"
    assert isinstance(first_call[2], float), "Timestamp should be recorded"

    second_call = session.metrics.tool_calls[1]
    assert second_call[0] == "FileRead", "Second tool should be FileRead"
    assert second_call[1]["path"] == "/test.txt", "Tool args should be preserved"

    third_call = session.metrics.tool_calls[2]
    assert third_call[0] == "Bash", "Third tool should be Bash"
    assert third_call[1]["command"] == "ls -la", "Tool args should be preserved"

    # Verify session duration tracking
    duration = session.get_duration()
    assert duration > 0, "Session should have positive duration"
    assert isinstance(duration, float), "Duration should be float (seconds)"

    # Verify session still active
    assert session.is_active() is True, "Session should still be active"
    assert session.status == "active", "Status should remain active"

    # CRITICAL: Metrics tracking is passive and doesn't interfere with execution


def test_safe_session_stop_request():
    """
    Test stop request works correctly.

    This test proves:
    - Stop request mechanism functions
    - Session status transitions correctly
    - Flags are set appropriately
    - Agent itself remains unchanged

    Philosophy: "Graceful interruption without breaking system"
    """
    # Create SafeSession with real agent
    session = SafeSession()
    agent = create_agency_code_agent(model="claude-haiku-4-5-20251001")
    session.set_agent(agent)

    # Verify initial active state
    assert session.is_active() is True, "Session should be active initially"
    assert session.stop_requested is False, "Stop should not be requested initially"
    assert session.status == "active", "Status should be active"

    # Request stop
    session.request_stop("Test stop")

    # Verify stop state
    assert session.is_active() is False, "Session should not be active after stop"
    assert session.stop_requested is True, "Stop flag should be set"
    assert session.status == "stopping", "Status should be 'stopping'"

    # Verify agent unchanged
    assert agent.name == "AgencyCodeAgent", "Agent should be unchanged"
    assert session._agent is agent, "Session should still reference agent"

    # Verify metrics still accessible
    assert session.metrics is not None, "Metrics should still be accessible"
    duration = session.get_duration()
    assert duration > 0, "Duration should still be calculable"

    # CRITICAL: Stop request is clean and doesn't break agent reference


def test_safe_session_with_planner_agent():
    """
    Additional test: Verify SafeSession works with PlannerAgent too.

    This test proves SafeSession is agent-agnostic and can wrap
    any Agency-Code agent without modification.

    Philosophy: "GRAFT onto existing, don't rebuild"
    """
    # Create planner agent
    planner = create_planner_agent(model="claude-haiku-4-5-20251001")

    # Verify planner created correctly
    assert planner is not None, "Planner should be created"
    assert planner.name == "PlannerAgent", "Planner should have correct name"

    # Wrap with SafeSession
    session = SafeSession()
    session.set_agent(planner)

    # Verify wrapping works
    assert session._agent is planner, "Session should reference planner"
    assert session._agent.name == "PlannerAgent", "Planner properties retained"
    assert session.is_active() is True, "Session should be active"

    # Verify planner unchanged
    assert planner.name == "PlannerAgent", "Planner should be unchanged"

    # CRITICAL: SafeSession is agent-agnostic and transparent


def test_safe_session_multiple_sessions_independent():
    """
    Additional test: Verify multiple SafeSessions are independent.

    This test proves:
    - Each session has unique ID
    - Sessions don't interfere with each other
    - Metrics are tracked independently

    Philosophy: "Isolation and independence"
    """
    # Create two agents
    agent1 = create_agency_code_agent(model="claude-haiku-4-5-20251001")
    agent2 = create_agency_code_agent(model="claude-haiku-4-5-20251001")

    # Create two sessions
    session1 = SafeSession()
    session2 = SafeSession()

    # Wrap different agents
    session1.set_agent(agent1)
    session2.set_agent(agent2)

    # Verify sessions are independent
    assert session1.session_id != session2.session_id, "Session IDs should be unique"
    assert session1._agent is agent1, "Session1 should reference agent1"
    assert session2._agent is agent2, "Session2 should reference agent2"

    # Record different tool calls
    session1.record_tool_call("ToolA", {"arg": "value1"})
    session2.record_tool_call("ToolB", {"arg": "value2"})
    session2.record_tool_call("ToolC", {"arg": "value3"})

    # Verify independent tracking
    assert len(session1.metrics.tool_calls) == 1, "Session1 should have 1 call"
    assert len(session2.metrics.tool_calls) == 2, "Session2 should have 2 calls"

    # Verify metrics don't interfere
    assert session1.metrics.total_tool_calls == 1, "Session1 count should be 1"
    assert session2.metrics.total_tool_calls == 2, "Session2 count should be 2"

    # Stop one session
    session1.request_stop()

    # Verify other session unaffected
    assert session1.is_active() is False, "Session1 should be stopped"
    assert session2.is_active() is True, "Session2 should still be active"

    # CRITICAL: Multiple sessions are completely independent


def test_agent_factory_without_session_parameter():
    """
    CRITICAL: Prove existing factory calls still work without session.

    This MUST pass - backward compatibility requirement.
    """
    from agency_code_agent.agency_code_agent import create_agency_code_agent

    # Create agent OLD WAY (no session parameter)
    agent = create_agency_code_agent(model="claude-haiku-4-5-20251001")

    # Should work exactly as before
    assert agent is not None
    assert agent.name == "AgencyCodeAgent"
    # This PROVES backward compatibility


def test_agent_factory_with_session_parameter():
    """
    Test factory accepts optional session parameter.
    """
    from agency_code_agent.agency_code_agent import create_agency_code_agent
    from safety.safe_session import SafeSession

    session = SafeSession()

    # Create agent NEW WAY (with session)
    agent = create_agency_code_agent(
        model="claude-haiku-4-5-20251001",
        session=session
    )

    # Agent should work
    assert agent is not None
    assert agent.name == "AgencyCodeAgent"
    assert session.session_id is not None


def test_planner_factory_with_session_parameter():
    """
    Test planner factory also accepts session parameter.
    """
    from planner_agent.planner_agent import create_planner_agent
    from safety.safe_session import SafeSession

    session = SafeSession()

    agent = create_planner_agent(
        model="claude-haiku-4-5-20251001",
        session=session
    )

    assert agent is not None
    assert agent.name == "PlannerAgent"
