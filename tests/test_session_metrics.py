import pytest
import time
from safety.session_metrics import SessionMetrics


def test_session_metrics_initialization():
    """Test SessionMetrics initializes with empty/default values"""
    metrics = SessionMetrics()

    assert metrics.tool_calls == []
    assert metrics.reasoning_steps == 0
    assert metrics.handoff_count == 0
    assert metrics.memory_peak == 0
    assert metrics.disk_used == 0
    assert isinstance(metrics.started_at, float)
    assert metrics.started_at > 0


def test_session_metrics_record_tool_call():
    """Test recording a tool call"""
    metrics = SessionMetrics()

    # Record a tool call
    metrics.record_tool_call("WebFetch", {"url": "example.com"})

    assert len(metrics.tool_calls) == 1
    assert metrics.tool_calls[0][0] == "WebFetch"
    assert metrics.tool_calls[0][1] == {"url": "example.com"}
    assert isinstance(metrics.tool_calls[0][2], float)  # timestamp


def test_session_metrics_get_duration():
    """Test getting session duration"""
    metrics = SessionMetrics()
    time.sleep(0.1)  # Sleep 100ms

    duration = metrics.get_duration()
    assert duration >= 0.1  # At least 100ms
    assert duration < 1.0   # Less than 1 second


def test_session_metrics_increment_reasoning():
    """Test incrementing reasoning step counter"""
    metrics = SessionMetrics()

    metrics.increment_reasoning_steps()
    assert metrics.reasoning_steps == 1

    metrics.increment_reasoning_steps()
    assert metrics.reasoning_steps == 2


def test_session_metrics_record_handoff():
    """Test recording agent handoff"""
    metrics = SessionMetrics()

    metrics.record_handoff("AgencyCodeAgent", "PlannerAgent")

    assert metrics.handoff_count == 1
    # Could also track which agents in future


def test_session_metrics_multiple_tool_calls():
    """Test recording multiple tool calls in sequence"""
    metrics = SessionMetrics()

    # Record multiple tool calls
    metrics.record_tool_call("BashTool", {"command": "ls"})
    time.sleep(0.01)  # Small delay to ensure different timestamps
    metrics.record_tool_call("ReadTool", {"file_path": "/test.py"})
    time.sleep(0.01)
    metrics.record_tool_call("WriteTool", {"file_path": "/output.txt", "content": "test"})

    # Verify all calls tracked
    assert len(metrics.tool_calls) == 3

    # Verify correct order and data
    assert metrics.tool_calls[0][0] == "BashTool"
    assert metrics.tool_calls[0][1] == {"command": "ls"}

    assert metrics.tool_calls[1][0] == "ReadTool"
    assert metrics.tool_calls[1][1] == {"file_path": "/test.py"}

    assert metrics.tool_calls[2][0] == "WriteTool"
    assert metrics.tool_calls[2][1] == {"file_path": "/output.txt", "content": "test"}

    # Verify timestamps are in chronological order
    assert metrics.tool_calls[0][2] < metrics.tool_calls[1][2]
    assert metrics.tool_calls[1][2] < metrics.tool_calls[2][2]
