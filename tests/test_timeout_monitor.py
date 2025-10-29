import pytest
import time
from safety.timeout_monitor import TimeoutConfig, TimeoutMonitor
from safety.safe_session import SafeSession


def test_timeout_config_initialization():
    """Test TimeoutConfig initializes with defaults"""
    config = TimeoutConfig()

    assert config.max_session_duration > 0
    assert config.warning_threshold_75 > 0
    assert config.warning_threshold_90 > 0


def test_timeout_config_custom_values():
    """Test TimeoutConfig accepts custom values"""
    config = TimeoutConfig(
        max_session_duration=600,  # 10 minutes
        turn_timeout=120,          # 2 minutes
        tool_timeout=30            # 30 seconds
    )

    assert config.max_session_duration == 600
    assert config.turn_timeout == 120
    assert config.tool_timeout == 30


def test_timeout_monitor_initialization():
    """Test TimeoutMonitor initializes with session"""
    session = SafeSession()
    config = TimeoutConfig(max_session_duration=100)
    monitor = TimeoutMonitor(session, config)

    assert monitor.session == session
    assert monitor.config == config
    assert monitor.warnings_sent == []


def test_timeout_monitor_no_timeout_within_limit():
    """Test monitor returns None when within time limit"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 50  # 50 seconds ago

    config = TimeoutConfig(max_session_duration=100)  # 100s limit
    monitor = TimeoutMonitor(session, config)

    warning = monitor.check_timeout()

    assert warning is None  # Should NOT warn yet


def test_timeout_monitor_warns_at_75_percent():
    """Test monitor warns at 75% of timeout"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 75  # 75 seconds ago

    config = TimeoutConfig(max_session_duration=100)
    monitor = TimeoutMonitor(session, config)

    warning = monitor.check_timeout()

    assert warning is not None
    assert "75%" in warning or "WARNING" in warning


def test_timeout_monitor_warns_at_90_percent():
    """Test monitor warns at 90% of timeout"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 90  # 90 seconds ago

    config = TimeoutConfig(max_session_duration=100)
    monitor = TimeoutMonitor(session, config)

    warning = monitor.check_timeout()

    assert warning is not None
    assert "90%" in warning or "WARNING" in warning


def test_timeout_monitor_detects_exceeded():
    """Test monitor detects when timeout exceeded"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 150  # 150 seconds ago

    config = TimeoutConfig(max_session_duration=100)
    monitor = TimeoutMonitor(session, config)

    warning = monitor.check_timeout()

    assert warning is not None
    assert "TIMEOUT" in warning or "exceeded" in warning


def test_timeout_monitor_is_passive():
    """
    CRITICAL: Monitor only observes, doesn't modify session or kill process
    """
    session = SafeSession()
    session.metrics.started_at = time.time() - 150  # Way over limit
    session.status = "active"

    config = TimeoutConfig(max_session_duration=100)
    monitor = TimeoutMonitor(session, config)

    # Check timeout
    warning = monitor.check_timeout()

    # Session unchanged
    assert session.status == "active"
    assert session._agent is None  # No process reference touched

    # Just returns warning string
    assert isinstance(warning, str)


def test_timeout_monitor_doesnt_warn_twice():
    """Test monitor doesn't send duplicate warnings"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 75

    config = TimeoutConfig(max_session_duration=100)
    monitor = TimeoutMonitor(session, config)

    # First check - should warn
    warning1 = monitor.check_timeout()
    assert warning1 is not None

    # Second check - should NOT warn again for same threshold
    warning2 = monitor.check_timeout()
    assert warning2 is None or "75%" not in warning2
