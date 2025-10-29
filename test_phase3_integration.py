"""Manual integration test for Phase 3"""
from safety import SafeSession, TimeoutConfig, TimeoutMonitor, RunawayDetector
import time

print("=== Phase 3 Integration Test ===\n")

# Create SafeSession with full Phase 3 components
session = SafeSession()
print(f"Session created: {session.session_id}\n")

# Add timeout monitoring
config = TimeoutConfig(max_session_duration=1800)  # 30 minutes
monitor = TimeoutMonitor(session, config)
print(f"TimeoutMonitor initialized (max: {config.max_session_duration}s)\n")

# Add runaway detection
detector = RunawayDetector(session)
print(f"RunawayDetector initialized\n")

# Simulate some activity
print("Simulating agent activity...")
session.metrics.record_tool_call("Bash", {"command": "ls"})
session.metrics.record_tool_call("Read", {"file": "test.txt"})
session.metrics.increment_reasoning_steps()
session.metrics.increment_reasoning_steps()

# Check status
print("\nChecking status...")
timeout_warning = monitor.check_timeout()
runaway_pattern = detector.detect_pattern()

print(f"  Timeout warning: {timeout_warning or 'None (OK)'}")
print(f"  Runaway pattern: {runaway_pattern or 'None (OK)'}")

# Session stats
print(f"\nSession stats:")
print(f"  Duration: {session.metrics.get_duration():.2f}s")
print(f"  Tool calls: {len(session.metrics.tool_calls)}")
print(f"  Reasoning steps: {session.metrics.reasoning_steps}")
print(f"  Handoffs: {session.metrics.handoff_count}")

print("\n=== Phase 3 integration test passed! ===")
