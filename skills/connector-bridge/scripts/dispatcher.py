#!/usr/bin/env python3
"""
Dispatcher
Bounded timeout + exponential backoff retry dispatcher with circuit breaker integration.
"""

import asyncio
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable, Awaitable, TypeVar
from dataclasses import dataclass
from enum import Enum
from functools import wraps

import httpx

# Import local modules
sys.path.insert(0, str(Path(__file__).parent))
from circuit_breaker import CircuitBreakerRegistry, CircuitBreakerConfig, CircuitBreakerOpenError
from rate_limiter import TokenBucket, DEFAULT_CONFIGS
from protocol_serializer import get_serializer, Protocol, SerializedRequest, BaseSerializer

T = TypeVar('T')


class RetryPolicy(Enum):
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    CONSTANT = "constant"
    NONE = "none"


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    policy: RetryPolicy = RetryPolicy.EXPONENTIAL
    jitter: float = 0.1
    retry_on: tuple = (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError)


@dataclass
class DispatchConfig:
    timeout: float = 30.0
    retry: RetryConfig = None
    circuit_breaker: bool = True
    rate_limit: bool = True
    serializer: Optional[str] = None


class Dispatcher:
    """Async dispatcher with timeout, retry, circuit breaker, and rate limiting."""
    
    def __init__(self, config: DispatchConfig = None):
        self.config = config or DispatchConfig()
        self.client = httpx.AsyncClient(timeout=self.config.timeout)
        self.circuit_registry = CircuitBreakerRegistry()
        self.rate_limiter = TokenBucket()
        self.serializer = None
        
        if self.config.serializer:
            self.serializer = get_serializer(self.config.serializer)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _should_retry(self, attempt: int, exception: Exception, config: RetryConfig) -> bool:
        if attempt >= config.max_attempts:
            return False
        if not isinstance(exception, config.retry_on):
            # Check for 5xx HTTP errors
            if hasattr(exception, 'response') and exception.response is not None:
                return 500 <= exception.response.status_code < 600
            return False
        return True
    
    def _calculate_delay(self, attempt: int, config: RetryConfig) -> float:
        if config.policy == RetryPolicy.EXPONENTIAL:
            delay = config.base_delay * (2 ** attempt)
        elif config.policy == RetryPolicy.LINEAR:
            delay = config.base_delay * (attempt + 1)
        else:  # CONSTANT
            delay = config.base_delay
        
        # Cap at max_delay
        delay = min(delay, config.max_delay)
        
        # Add jitter
        jitter_range = delay * config.jitter
        return delay + random.uniform(-jitter_range, jitter_range)
    
    async def dispatch(self, request: SerializedRequest, endpoint: str = None, 
                       retry_config: RetryConfig = None, cb_config: CircuitBreakerConfig = None) -> httpx.Response:
        """Dispatch a serialized request with all protections."""
        retry_config = retry_config or self.config.retry or RetryConfig()
        cb_config = cb_config or CircuitBreakerConfig()
        
        last_exception = None
        
        for attempt in range(retry_config.max_attempts):
            try:
                # Rate limiting
                if self.config.rate_limit and endpoint:
                    await self._acquire_rate_limit(endpoint)
                
                # Circuit breaker
                if self.config.circuit_breaker and endpoint:
                    cb = self.circuit_registry.get_or_create(endpoint, CircuitBreakerConfig())
                    return await cb.call(self._make_request, request)
                else:
                    return await self._make_request(request)
                    
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(attempt, e, retry_config):
                    raise
                
                delay = self._calculate_delay(attempt, retry_config)
                await asyncio.sleep(delay)
        
        raise last_exception
    
    async def _make_request(self, request: SerializedRequest) -> httpx.Response:
        """Make the actual HTTP request."""
        kwargs = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
        }
        
        if request.body:
            kwargs["content"] = request.body
        if request.params:
            kwargs["params"] = request.params
        
        return await self.client.request(**kwargs)
    
    async def _acquire_rate_limit(self, endpoint: str):
        """Acquire rate limit token (async wrapper)."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.rate_limiter.acquire, endpoint, 1, True, 30.0)
    
    def dispatch_sync(self, request: SerializedRequest, endpoint: str = None,
                      retry_config: RetryConfig = None) -> httpx.Response:
        """Synchronous dispatch wrapper."""
        return asyncio.run(self.dispatch(request, endpoint, retry_config))
    
    async def dispatch_with_serializer(self, protocol: str, operation: str, 
                                       payload: Dict, config: Dict, endpoint: str = None) -> httpx.Response:
        """Dispatch with automatic serialization."""
        serializer = get_serializer(protocol)
        request = serializer.serialize(operation, payload, config)
        return await self.dispatch(request, endpoint)


# Global dispatcher instance
DISPATCHER = Dispatcher()


async def main_async():
    """Async entry point for testing."""
    if len(sys.argv) < 3:
        print("Usage: dispatcher.py <url> <method> [json_body]")
        return
    
    url = sys.argv[1]
    method = sys.argv[2].upper()
    body = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    
    request = SerializedRequest(
        method=method,
        url=url,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        body=json.dumps(body) if body else None,
        params=None
    )
    
    async with Dispatcher() as dispatcher:
        response = await dispatcher.dispatch(request)
        print(f"Status: {response.status_code}")
        print(json.dumps(response.json(), indent=2) if response.content else "No content")


def main():
    if len(sys.argv) < 2:
        print("Usage: dispatcher.py <command> [args...]")
        print("Commands:")
        print("  request <url> <method> [body]  - Make HTTP request")
        print("  test <url>                     - Test dispatch with retries")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "request":
        if len(sys.argv) < 4:
            print("Usage: dispatcher.py request <url> <method> [body_json]")
            sys.exit(1)
        asyncio.run(main_async())
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("Usage: dispatcher.py test <url>")
            sys.exit(1)
        
        # Test with retries
        request = SerializedRequest(
            method="GET",
            url=sys.argv[2],
            headers={"Accept": "application/json"},
            body=None,
            params=None
        )
        
        retry_config = RetryConfig(max_attempts=3, base_delay=0.5, policy=RetryPolicy.EXPONENTIAL)
        config = DispatchConfig(retry=retry_config)
        dispatcher = Dispatcher(config)
        
        async def run_test():
            async with dispatcher:
                for i in range(5):
                    try:
                        resp = await dispatcher.dispatch(request)
                        print(f"Attempt {i+1}: {resp.status_code}")
                    except Exception as e:
                        print(f"Attempt {i+1}: FAILED - {e}")
        
        asyncio.run(run_test())
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
