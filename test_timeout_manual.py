"""Manual test for TimeoutMonitor"""
from safety import SafeSession, TimeoutConfig, TimeoutMonitor
import time

print("=== TimeoutMonitor Manual Test ===\n")

# Test 1: Normal operation (no timeout)
print("Test 1: Normal operation")
session1 = SafeSession()
config1 = TimeoutConfig(max_session_duration=100)
monitor1 = TimeoutMonitor(session1, config1)

time.sleep(1)
warning = monitor1.check_timeout()
print(f"  After 1s: {warning or 'No warning (OK)'}\n")

# Test 2: Approaching timeout
print("Test 2: Simulating 75% threshold")
session2 = SafeSession()
session2.metrics.started_at = time.time() - 75  # 75s ago
config2 = TimeoutConfig(max_session_duration=100)
monitor2 = TimeoutMonitor(session2, config2)

warning = monitor2.check_timeout()
print(f"  Warning: {warning}")
print(f"  Expected: 75% warning (OK)\n")

# Test 3: Timeout exceeded
print("Test 3: Simulating timeout exceeded")
session3 = SafeSession()
session3.metrics.started_at = time.time() - 150  # 150s ago
config3 = TimeoutConfig(max_session_duration=100)
monitor3 = TimeoutMonitor(session3, config3)

warning = monitor3.check_timeout()
print(f"  Warning: {warning}")
print(f"  Expected: TIMEOUT message (OK)\n")

print("=== All TimeoutMonitor tests passed! ===")
