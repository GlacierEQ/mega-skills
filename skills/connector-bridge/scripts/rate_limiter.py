#!/usr/bin/env python3
"""
Rate Limiter
Token bucket rate limiter with per-endpoint ceilings and token quota tracking.
"""

import time
import threading
import json
import sys
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class RateLimitConfig:
    requests_per_second: float
    burst: int
    daily_quota: Optional[int] = None


@dataclass
class EndpointState:
    tokens: float
    last_update: float
    daily_used: int = 0
    daily_reset: float = field(default_factory=lambda: time.time() + 86400)


# Default rate limit configs for known services
DEFAULT_CONFIGS = {
    "openrouter": RateLimitConfig(requests_per_second=10, burst=20, daily_quota=1000),
    "github": RateLimitConfig(requests_per_second=5, burst=10, daily_quota=5000),
    "deepseek": RateLimitConfig(requests_per_second=5, burst=10, daily_quota=1000),
    "groq": RateLimitConfig(requests_per_second=30, burst=50, daily_quota=5000),
    "anthropic": RateLimitConfig(requests_per_second=5, burst=10, daily_quota=1000),
    "openai": RateLimitConfig(requests_per_second=10, burst=20, daily_quota=3000),
    "groq": RateLimitConfig(requests_per_second=30, burst=50, daily_quota=5000),
    "perplexity": RateLimitConfig(requests_per_second=5, burst=10, daily_quota=500),
    "cohere": RateLimitConfig(requests_per_second=10, burst=20, daily_quota=1000),
    "supabase": RateLimitConfig(requests_per_second=50, burst=100, daily_quota=10000),
    "pinecone": RateLimitConfig(requests_per_second=100, burst=200, daily_quota=10000),
}


class TokenBucket:
    """Thread-safe token bucket rate limiter."""
    
    def __init__(self, configs: Dict[str, RateLimitConfig] = None):
        self.configs = configs or DEFAULT_CONFIGS
        self.states: Dict[str, EndpointState] = {}
        self.lock = threading.RLock()
        
        # Initialize states
        for endpoint, config in self.configs.items():
            self.states[endpoint] = EndpointState(
                tokens=float(config.burst),
                last_update=time.time()
            )
    
    def _refill(self, endpoint: str):
        """Refill tokens based on elapsed time."""
        config = self.configs.get(endpoint)
        if not config:
            return
        
        state = self.states[endpoint]
        now = time.time()
        
        # Check daily reset
        if now >= state.daily_reset:
            state.daily_used = 0
            state.daily_reset = now + 86400
        
        # Refill tokens
        elapsed = now - state.last_update
        new_tokens = elapsed * config.requests_per_second
        state.tokens = min(config.burst, state.tokens + new_tokens)
        state.last_update = now
    
    def acquire(self, endpoint: str, tokens: int = 1, blocking: bool = True, timeout: float = 30.0) -> bool:
        """Acquire tokens from the bucket."""
        if endpoint not in self.configs:
            # Unknown endpoint - allow but track
            if endpoint not in self.states:
                self.states[endpoint] = EndpointState(tokens=float('inf'), last_update=time.time())
            return True
        
        config = self.configs[endpoint]
        state = self.states[endpoint]
        
        # Check daily quota
        if config.daily_quota and state.daily_used >= config.daily_quota:
            return False
        
        start = time.time()
        while True:
            with self.lock:
                self._refill(endpoint)
                
                if state.tokens >= tokens:
                    state.tokens -= tokens
                    if config.daily_quota:
                        state.daily_used += tokens
                    return True
            
            if not blocking:
                return False
            
            if time.time() - start > timeout:
                return False
            
            # Wait for next token
            time.sleep(0.01)
    
    def get_status(self, endpoint: str) -> Dict:
        """Get current rate limit status."""
        with self.lock:
            self._refill(endpoint)
            state = self.states.get(endpoint)
            config = self.configs.get(endpoint)
            
            if not state or not config:
                return {"endpoint": endpoint, "configured": False}
            
            return {
                "endpoint": endpoint,
                "configured": True,
                "tokens_available": round(state.tokens, 2),
                "max_burst": config.burst,
                "rate_per_sec": config.requests_per_second,
                "daily_used": state.daily_used,
                "daily_quota": config.daily_quota,
                "daily_remaining": max(0, config.daily_quota - state.daily_used) if config.daily_quota else None
            }
    
    def get_all_status(self) -> Dict[str, Dict]:
        """Get status for all configured endpoints."""
        return {ep: self.get_status(ep) for ep in self.configs}


def main():
    if len(sys.argv) < 2:
        print("Usage: rate_limiter.py <command> [args...]")
        print("Commands:")
        print("  status <endpoint>          - Show rate limit status")
        print("  status-all                 - Show all endpoints status")
        print("  acquire <endpoint> [N]     - Acquire N tokens (default 1)")
        print("  wait <endpoint> [timeout]  - Wait until token available")
        sys.exit(1)
    
    bucket = TokenBucket()
    command = sys.argv[1]
    
    if command == "status":
        if len(sys.argv) < 3:
            print("Usage: rate_limiter.py status <endpoint>")
            sys.exit(1)
        print(json.dumps(bucket.get_status(sys.argv[2]), indent=2))
    
    elif command == "status-all":
        print(json.dumps(bucket.get_all_status(), indent=2))
    
    elif command == "acquire":
        if len(sys.argv) < 3:
            print("Usage: rate_limiter.py acquire <endpoint> [tokens]")
            sys.exit(1)
        endpoint = sys.argv[2]
        tokens = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        success = bucket.acquire(endpoint, tokens)
        print(f"Acquired {tokens} tokens for {endpoint}: {success}")
        sys.exit(0 if success else 1)
    
    elif command == "wait":
        if len(sys.argv) < 3:
            print("Usage: rate_limiter.py wait <endpoint> [timeout]")
            sys.exit(1)
        endpoint = sys.argv[2]
        timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
        success = bucket.acquire(endpoint, 1, blocking=True, timeout=timeout)
        print(f"Waited for {endpoint}: {success}")
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
