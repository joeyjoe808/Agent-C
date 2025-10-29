import pytest
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
