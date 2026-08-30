#!/usr/bin/env python3
"""
Circuit Breaker
State machine for fault tolerance with automatic recovery.
"""

import time
import threading
import json
import sys
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps


class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5          # Failures to trip
    success_threshold: int = 2          # Successes to close from half-open
    timeout: float = 30.0               # Seconds before half-open
    excluded_exceptions: tuple = ()     # Exceptions that don't count


@dataclass
class CircuitStats:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: float = 0
    last_state_change: float = 0


class CircuitBreaker:
    """Thread-safe circuit breaker with configurable thresholds."""
    
    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self.lock = threading.RLock()
    
    def _transition_to(self, new_state: CircuitState):
        self.state = new_state
        self.stats.last_state_change = time.time()
    
    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        with self.lock:
            self.stats.total_calls += 1
            
            # Check if we should allow the call
            if self.state == CircuitState.OPEN:
                if time.time() - self.stats.last_failure_time >= self.config.timeout:
                    # Transition to half-open
                    self._transition_to(CircuitState.HALF_OPEN)
                else:
                    raise CircuitBreakerOpenError(f"Circuit {self.name} is OPEN")
            
            # Allow call in CLOSED or HALF_OPEN
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.config.excluded_exceptions:
                # Excluded exceptions don't count as failures
                raise
            except Exception as e:
                self._on_failure()
                raise
    
    def _on_success(self):
        with self.lock:
            self.stats.successful_calls += 1
            self.stats.consecutive_failures = 0
            self.stats.consecutive_successes += 1
            
            if self.state == CircuitState.HALF_OPEN:
                if self.stats.consecutive_successes >= self.config.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
    
    def _on_failure(self):
        with self.lock:
            self.stats.failed_calls += 1
            self.stats.consecutive_failures += 1
            self.stats.consecutive_successes = 0
            self.stats.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open goes back to open
                self._transition_to(CircuitState.OPEN)
            elif self.state == CircuitState.CLOSED:
                if self.stats.consecutive_failures >= self.config.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
    
    def get_status(self) -> Dict:
        with self.lock:
            return {
                "name": self.name,
                "state": self.state.value,
                "stats": {
                    "total_calls": self.stats.total_calls,
                    "successful_calls": self.stats.successful_calls,
                    "failed_calls": self.stats.failed_calls,
                    "consecutive_failures": self.stats.consecutive_failures,
                    "consecutive_successes": self.stats.consecutive_successes,
                    "success_rate": round(
                        self.stats.successful_calls / max(1, self.stats.total_calls), 4
                    ),
                    "last_state_change": self.stats.last_state_change,
                    "time_in_current_state": time.time() - self.stats.last_state_change
                }
            }
    
    def reset(self):
        """Manually reset the circuit breaker."""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.stats = CircuitStats()


class CircuitBreakerRegistry:
    """Registry of circuit breakers for multiple endpoints."""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.lock = threading.RLock()
    
    def get_or_create(self, name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
        with self.lock:
            if name not in self.breakers:
                self.breakers[name] = CircuitBreaker(name, config)
            return self.breakers[name]
    
    def get_status(self, name: str) -> Optional[Dict]:
        with self.lock:
            if name in self.breakers:
                return self.breakers[name].get_status()
        return None
    
    def get_all_status(self) -> Dict[str, Dict]:
        with self.lock:
            return {name: b.get_status() for name, b in self.breakers.items()}
    
    def execute(self, name: str, func: Callable, *args, config: CircuitBreakerConfig = None, **kwargs):
        """Execute function with circuit breaker protection."""
        breaker = self.get_or_create(name, config)
        return breaker.call(func, *args, **kwargs)


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Global registry
REGISTRY = CircuitBreakerRegistry()


def with_circuit_breaker(name: str, config: CircuitBreakerConfig = None):
    """Decorator to add circuit breaker to a function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return REGISTRY.execute(name, func, *args, config=config, **kwargs)
        return wrapper
    return decorator


def main():
    if len(sys.argv) < 2:
        print("Usage: circuit_breaker.py <command> [args...]")
        print("Commands:")
        print("  status <name>        - Show circuit breaker status")
        print("  status-all           - Show all breakers status")
        print("  reset <name>         - Reset circuit breaker")
        print("  test <name> <failures> - Simulate failures to trip breaker")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        if len(sys.argv) < 3:
            print("Usage: circuit_breaker.py status <name>")
            sys.exit(1)
        status = REGISTRY.get_status(sys.argv[2])
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"No circuit breaker named {sys.argv[2]}")
    
    elif command == "status-all":
        print(json.dumps(REGISTRY.get_all_status(), indent=2))
    
    elif command == "reset":
        if len(sys.argv) < 3:
            print("Usage: circuit_breaker.py reset <name>")
            sys.exit(1)
        REGISTRY.get_or_create(sys.argv[2]).reset()
        print(f"Reset {sys.argv[2]}")
    
    elif command == "test":
        if len(sys.argv) < 4:
            print("Usage: circuit_breaker.py test <name> <failures>")
            sys.exit(1)
        name = sys.argv[2]
        failures = int(sys.argv[3])
        
        @with_circuit_breaker(name, CircuitBreakerConfig(failure_threshold=3))
        def failing_func():
            raise Exception("Simulated failure")
        
        for i in range(failures):
            try:
                failing_func()
            except Exception:
                pass
        
        status = REGISTRY.get_status(name)
        print(json.dumps(status, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
