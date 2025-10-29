import pytest
import time
import threading
from safety import SafeSession, TimeoutConfig
from safety.background_monitor import BackgroundMonitor, MonitorEvent, EventType


def test_background_monitor_initialization():
    """Test BackgroundMonitor initializes correctly"""
    session = SafeSession()
    config = TimeoutConfig(max_session_duration=100)
    monitor = BackgroundMonitor(session, config)

    assert monitor.session == session
    assert monitor.config == config
    assert monitor.is_running == False
    assert monitor.on_event is None


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
    assert any(e.event_type == EventType.TIMEOUT.value for e in events)


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
    assert any(e.event_type == EventType.RUNAWAY.value for e in events)


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


def test_monitor_event_structure():
    """Test MonitorEvent has expected structure"""
    event = MonitorEvent(
        event_type=EventType.TIMEOUT.value,
        message="Test timeout",
        severity="high",
        data={"elapsed": 100}
    )

    assert event.event_type == "timeout"
    assert event.message == "Test timeout"
    assert event.severity == "high"
    assert event.data["elapsed"] == 100


def test_auto_terminate_on_timeout():
    """Test monitor auto-terminates session on timeout when enabled"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 150  # 150s ago

    config = TimeoutConfig(max_session_duration=100)  # 100s limit
    monitor = BackgroundMonitor(session, config, check_interval=0.1, auto_terminate=True)

    monitor.start()
    time.sleep(0.5)  # Wait for check
    monitor.stop()

    # Session should be terminated
    assert session.status == "terminated"
    assert session.stop_requested == True


def test_auto_terminate_on_runaway():
    """Test monitor auto-terminates session on runaway pattern when enabled"""
    session = SafeSession()

    # Simulate infinite tool loop
    for _ in range(6):
        session.metrics.record_tool_call("Bash", {})

    config = TimeoutConfig()
    monitor = BackgroundMonitor(session, config, check_interval=0.1, auto_terminate=True)

    monitor.start()
    time.sleep(0.5)  # Wait for check
    monitor.stop()

    # Session should be terminated
    assert session.status == "terminated"
    assert session.stop_requested == True


def test_no_auto_terminate_when_disabled():
    """Test monitor does NOT auto-terminate when disabled (default)"""
    session = SafeSession()
    session.metrics.started_at = time.time() - 150  # 150s ago

    config = TimeoutConfig(max_session_duration=100)  # 100s limit
    monitor = BackgroundMonitor(session, config, check_interval=0.1, auto_terminate=False)

    events = []
    def on_event(event: MonitorEvent):
        events.append(event)

    monitor.on_event = on_event
    monitor.start()
    time.sleep(0.5)  # Wait for check
    monitor.stop()

    # Should detect timeout but NOT terminate
    assert len(events) > 0
    assert any(e.event_type == EventType.TIMEOUT.value for e in events)
    assert session.status != "terminated"  # Still active
    assert session.stop_requested == False
