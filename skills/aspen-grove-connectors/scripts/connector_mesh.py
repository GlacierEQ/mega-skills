#!/usr/bin/env python3
"""Aspen Grove connector mesh with evidence-safe provider semantics."""

from __future__ import annotations

import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Optional

HealthProbe = Callable[[], Dict[str, Any]]
RequestHandler = Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]]


class BaseConnector:
    """Connector envelope. Configuration is never treated as provider verification."""

    def __init__(
        self,
        service_name: str,
        mock_mode: bool = False,
        health_probe: Optional[HealthProbe] = None,
        request_handler: Optional[RequestHandler] = None,
    ):
        self.service_name = service_name
        self.mock_mode = mock_mode
        self.health_probe = health_probe
        self.request_handler = request_handler
        self.secret_token = self._resolve_secret()

    def _resolve_secret(self) -> Optional[str]:
        env_key = f"{self.service_name.upper()}_API_KEY"
        if env_key in os.environ:
            return os.environ[env_key]
        secret_file = Path.home() / ".secrets" / self.service_name
        if secret_file.exists():
            return secret_file.read_text(encoding="utf-8").strip()
        return None

    def health_check(self) -> Dict[str, Any]:
        base = {
            "service": self.service_name,
            "authenticated": bool(self.secret_token),
            "verified": False,
        }
        if self.mock_mode:
            return {
                **base,
                "status": "sandbox_mock",
                "evidence_state": "SIMULATED",
                "reason": "mock_mode_enabled",
            }
        if self.health_probe is None:
            return {
                **base,
                "status": "configured_unverified" if self.secret_token else "unconfigured",
                "evidence_state": "UNVERIFIED",
                "reason": (
                    "credential_present_without_provider_probe"
                    if self.secret_token
                    else "no_credential_or_provider_probe"
                ),
            }

        try:
            receipt = self.health_probe()
        except Exception as exc:
            return {
                **base,
                "status": "probe_failed",
                "evidence_state": "ATTEMPTED",
                "reason": f"{type(exc).__name__}: {exc}",
            }

        if not isinstance(receipt, dict):
            return {
                **base,
                "status": "probe_unverified",
                "evidence_state": "SOURCE_BOUND",
                "reason": "provider_probe_returned_non_mapping_receipt",
            }

        verified = receipt.get("verified") is True
        return {
            **base,
            "status": "verified_live" if verified else "probe_unverified",
            "evidence_state": "VERIFIED" if verified else "SOURCE_BOUND",
            "verified": verified,
            "provider_receipt": receipt,
        }

    def execute_request(
        self,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        if self.mock_mode:
            return {
                "status": "simulated_success",
                "mode": "mock",
                "service": self.service_name,
                "endpoint": endpoint,
                "data": {"mock_result": f"Simulated data for {endpoint}", "payload": payload or {}},
                "digest": hashlib.sha256(f"{self.service_name}:{endpoint}".encode()).hexdigest(),
                "verified": False,
                "evidence_state": "SIMULATED",
            }

        if self.request_handler is None:
            return {
                "status": "blocked",
                "mode": "unbound",
                "service": self.service_name,
                "endpoint": endpoint,
                "verified": False,
                "evidence_state": "UNVERIFIED",
                "reason": "live_transport_unbound",
            }

        for attempt in range(1, max_retries + 1):
            try:
                receipt = self.request_handler(endpoint, payload)
                if not isinstance(receipt, dict):
                    return {
                        "status": "completed_unverified",
                        "mode": "bound",
                        "service": self.service_name,
                        "endpoint": endpoint,
                        "verified": False,
                        "evidence_state": "SOURCE_BOUND",
                        "reason": "provider_handler_returned_non_mapping_receipt",
                    }
                verified = receipt.get("verified") is True
                return {
                    "status": "verified_success" if verified else "completed_unverified",
                    "mode": "bound",
                    "service": self.service_name,
                    "endpoint": endpoint,
                    "verified": verified,
                    "evidence_state": "VERIFIED" if verified else "SOURCE_BOUND",
                    "provider_receipt": receipt,
                }
            except Exception as exc:
                if attempt == max_retries:
                    return {
                        "status": "error",
                        "service": self.service_name,
                        "endpoint": endpoint,
                        "verified": False,
                        "evidence_state": "ATTEMPTED",
                        "reason": f"{type(exc).__name__}: {exc}",
                        "attempts": attempt,
                    }
                time.sleep(0.05 * (2**attempt) + random.uniform(0.01, 0.03))

        return {
            "status": "error",
            "service": self.service_name,
            "verified": False,
            "evidence_state": "ATTEMPTED",
            "reason": "retry_loop_exhausted",
        }


class AspenGroveMesh:
    SERVICES = [
        "github", "notion", "supabase", "dropbox", "linear", "clickup",
        "vercel", "duckdb", "pinecone", "taskade", "gmail", "google_drive",
        "slack", "memoryplugin", "mem0", "e2b",
    ]

    def __init__(
        self,
        force_mock: bool = False,
        services: Optional[Iterable[str]] = None,
        connectors: Optional[Dict[str, BaseConnector]] = None,
    ):
        selected = list(dict.fromkeys(services or self.SERVICES))
        self.force_mock = force_mock
        self.connectors: Dict[str, BaseConnector] = {
            service: BaseConnector(service, mock_mode=force_mock) for service in selected
        }
        if connectors:
            self.connectors.update(connectors)

    def get_connector(self, service: str) -> BaseConnector:
        if service not in self.connectors:
            raise KeyError(
                f"Unknown service connector: {service}. "
                f"Available: {sorted(self.connectors)}"
            )
        return self.connectors[service]

    def health_all(self) -> Dict[str, Any]:
        return {name: connector.health_check() for name, connector in self.connectors.items()}

    def dispatch(
        self,
        service: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.get_connector(service).execute_request(endpoint, payload)

    def plan_pipeline(self, stages: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate whether a connector coalition has enough evidence to run."""
        planned = []
        blocked = []
        for index, stage in enumerate(stages):
            service = str(stage["service"])
            required_verified = bool(stage.get("required_verified", True))
            health = self.get_connector(service).health_check()
            row = {
                "index": index,
                "service": service,
                "required_verified": required_verified,
                "health": health,
            }
            planned.append(row)
            if required_verified and health.get("verified") is not True:
                blocked.append({
                    "index": index,
                    "service": service,
                    "reason": "provider_not_verified",
                    "evidence_state": health.get("evidence_state", "UNVERIFIED"),
                })
        return {
            "status": "ready" if not blocked else "blocked",
            "runnable": not blocked,
            "stages": planned,
            "blocked": blocked,
        }


def main() -> int:
    mesh = AspenGroveMesh(force_mock=True)
    health = mesh.health_all()
    print(json.dumps({
        "skill": "aspen-grove-connectors",
        "status": "ready",
        "firewall_active": True,
        "connector_count": len(health),
        "verification_semantics": (
            "Mock, configured, or credential-present states are never provider verified. "
            "Only explicit provider receipts may set verified=true."
        ),
        "health_summary": health,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
