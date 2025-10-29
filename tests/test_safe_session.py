import pytest
from safety.safe_session import SafeSession
from safety.session_metrics import SessionMetrics


def test_safe_session_initialization():
    """Test SafeSession initializes correctly"""
    session = SafeSession()

    assert session.session_id is not None
    assert len(session.session_id) > 0
    assert isinstance(session.metrics, SessionMetrics)
    assert session.stop_requested == False
    assert session.status == "initializing"


def test_safe_session_is_transparent_wrapper():
    """CRITICAL: SafeSession doesn't interfere with wrapped object"""
    session = SafeSession()

    # Mock agent
    class MockAgent:
        name = "TestAgent"

        def execute(self):
            return "result"

    mock_agent = MockAgent()
    session.set_agent(mock_agent)

    # Agent should work exactly as before
    assert session._agent == mock_agent
    assert session._agent.name == "TestAgent"
    assert session._agent.execute() == "result"


def test_safe_session_tracks_tool_calls():
    """Test SafeSession tracks tool calls passively"""
    session = SafeSession()

    # Record some tool calls
    session.record_tool_call("WebFetch", {"url": "example.com"})
    session.record_tool_call("FileRead", {"path": "/test"})

    assert len(session.metrics.tool_calls) == 2
    assert session.metrics.tool_calls[0][0] == "WebFetch"
    assert session.metrics.tool_calls[1][0] == "FileRead"


def test_safe_session_request_stop():
    """Test requesting session stop"""
    session = SafeSession()

    assert session.stop_requested == False

    session.request_stop("User requested stop")

    assert session.stop_requested == True
    assert session.status == "stopping"


def test_safe_session_unique_ids():
    """Test each session has unique ID"""
    session1 = SafeSession()
    session2 = SafeSession()

    assert session1.session_id != session2.session_id
