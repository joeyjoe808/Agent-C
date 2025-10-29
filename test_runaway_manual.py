"""Manual test for RunawayDetector"""
from safety import SafeSession, RunawayDetector, RunawayPattern

print("=== RunawayDetector Manual Test ===\n")

# Test 1: Normal operation
print("Test 1: Normal operation (varied tools)")
session1 = SafeSession()
session1.metrics.record_tool_call("Bash", {})
session1.metrics.record_tool_call("Read", {})
session1.metrics.record_tool_call("Write", {})

detector1 = RunawayDetector(session1)
pattern = detector1.detect_pattern()
print(f"  Pattern: {pattern or 'None (OK)'}\n")

# Test 2: Infinite tool loop
print("Test 2: Infinite tool loop (6 same tool calls)")
session2 = SafeSession()
for _ in range(6):
    session2.metrics.record_tool_call("Bash", {})

detector2 = RunawayDetector(session2)
pattern = detector2.detect_pattern()
message = detector2.get_detection_message(pattern)
print(f"  Pattern: {pattern}")
print(f"  Message: {message}")
print(f"  Expected: INFINITE_TOOL_LOOP (OK)\n")

# Test 3: Excessive reasoning
print("Test 3: Excessive reasoning (60 steps)")
session3 = SafeSession()
session3.metrics.reasoning_steps = 60

detector3 = RunawayDetector(session3)
pattern = detector3.detect_pattern()
message = detector3.get_detection_message(pattern)
print(f"  Pattern: {pattern}")
print(f"  Message: {message}")
print(f"  Expected: EXCESSIVE_REASONING (OK)\n")

# Test 4: Escalation spiral
print("Test 4: Escalation spiral (12 handoffs)")
session4 = SafeSession()
for i in range(12):
    session4.metrics.record_handoff("AgentA", "AgentB")

detector4 = RunawayDetector(session4)
pattern = detector4.detect_pattern()
message = detector4.get_detection_message(pattern)
print(f"  Pattern: {pattern}")
print(f"  Message: {message}")
print(f"  Expected: ESCALATION_SPIRAL (OK)\n")

print("=== All RunawayDetector tests passed! ===")
