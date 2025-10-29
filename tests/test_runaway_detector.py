import pytest
from safety.runaway_detector import RunawayDetector, RunawayPattern
from safety.safe_session import SafeSession


def test_runaway_pattern_enum():
    """Test RunawayPattern enum exists with expected values"""
    assert RunawayPattern.INFINITE_TOOL_LOOP is not None
    assert RunawayPattern.EXCESSIVE_REASONING is not None
    assert RunawayPattern.ESCALATION_SPIRAL is not None


def test_runaway_detector_initialization():
    """Test RunawayDetector initializes with session"""
    session = SafeSession()
    detector = RunawayDetector(session)

    assert detector.session == session
    assert detector.same_tool_threshold > 0
    assert detector.reasoning_threshold > 0
    assert detector.handoff_threshold > 0


def test_no_detection_on_normal_operation():
    """Test detector returns None for normal operation"""
    session = SafeSession()

    # Normal varied tool usage
    session.metrics.record_tool_call("Bash", {})
    session.metrics.record_tool_call("Read", {})
    session.metrics.record_tool_call("Write", {})
    session.metrics.record_tool_call("Edit", {})

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()

    assert pattern is None  # Should NOT detect anything


def test_detects_infinite_tool_loop():
    """Test detector finds same tool called 5+ times"""
    session = SafeSession()

    # Simulate 5 Bash calls in a row
    for _ in range(5):
        session.metrics.record_tool_call("Bash", {})

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()

    assert pattern == RunawayPattern.INFINITE_TOOL_LOOP


def test_no_false_positive_on_varied_tools():
    """CRITICAL: Different tools don't trigger false positive"""
    session = SafeSession()

    # Many tool calls but all different
    session.metrics.record_tool_call("Bash", {})
    session.metrics.record_tool_call("Read", {})
    session.metrics.record_tool_call("Write", {})
    session.metrics.record_tool_call("Edit", {})
    session.metrics.record_tool_call("Glob", {})
    session.metrics.record_tool_call("Grep", {})

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()

    assert pattern is None  # Should NOT detect runaway


def test_detects_excessive_reasoning():
    """Test detector finds excessive reasoning"""
    session = SafeSession()
    session.metrics.reasoning_steps = 51  # Over default threshold

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()

    assert pattern == RunawayPattern.EXCESSIVE_REASONING


def test_detects_escalation_spiral():
    """Test detector finds too many handoffs"""
    session = SafeSession()

    # Simulate 11 handoffs
    for i in range(11):
        if i % 2 == 0:
            session.metrics.record_handoff("PlannerAgent", "AgencyCodeAgent")
        else:
            session.metrics.record_handoff("AgencyCodeAgent", "PlannerAgent")

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()

    assert pattern == RunawayPattern.ESCALATION_SPIRAL


def test_detector_is_passive():
    """CRITICAL: Detector only observes, doesn't modify"""
    session = SafeSession()

    # Add some tool calls
    for _ in range(10):
        session.metrics.record_tool_call("Bash", {})

    original_call_count = len(session.metrics.tool_calls)

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()

    # Detector doesn't modify metrics
    assert len(session.metrics.tool_calls) == original_call_count

    # Just returns pattern enum
    assert isinstance(pattern, RunawayPattern)


def test_get_detection_message():
    """Test detector provides human-readable messages"""
    session = SafeSession()

    # Trigger infinite loop detection
    for _ in range(5):
        session.metrics.record_tool_call("Bash", {})

    detector = RunawayDetector(session)
    pattern = detector.detect_pattern()
    message = detector.get_detection_message(pattern)

    assert isinstance(message, str)
    assert len(message) > 0
    assert "tool" in message.lower() or "loop" in message.lower()


def test_custom_thresholds():
    """Test detector accepts custom thresholds"""
    session = SafeSession()

    # Only 3 same tool calls
    for _ in range(3):
        session.metrics.record_tool_call("Bash", {})

    # Default threshold (5) - should NOT detect
    detector1 = RunawayDetector(session)
    assert detector1.detect_pattern() is None

    # Custom threshold (3) - SHOULD detect
    detector2 = RunawayDetector(session, same_tool_threshold=3)
    assert detector2.detect_pattern() == RunawayPattern.INFINITE_TOOL_LOOP
