#!/usr/bin/env python3
"""Executable routing policy for the GlacierEQ plugin-expansion worker."""

from __future__ import annotations

from typing import Any, Dict, Optional


RULES = {
    "provider_evidence_over_stale_projection": True,
    "verified_core_requires_regression_signal": True,
    "same_route_retry_requires_material_change": True,
    "blockers_change_route_not_objective": True,
    "writes_require_provider_readback_for_promotion": True,
    "verification_scope_must_match_exercised_surface": True,
    "ambiguous_account_binding_must_not_be_guessed": True,
    "security_mutations_require_access_path_preservation": True,
    "stale_failed_deployment_requires_source_comparison_before_repair": True,
    "every_run_requires_material_delta": True,
    "authority_domains_must_not_be_collapsed": True,
    "retrieval_failure_is_not_absence": True,
    "fallback_equivalence_requires_capability_parity": True,
    "protected_projection_fields_must_survive": True,
    "reversible_mutations_require_prestate": True,
    "demotion_requires_disconfirming_evidence": True,
    "privacy_boundary_must_not_silently_widen": True,
}

EVIDENCE_RANK = {
    "UNVERIFIED": 0,
    "OBSERVED": 1,
    "OBSERVED_RUNTIME_EXPOSURE": 1,
    "INFERRED": 1,
    "ATTEMPTED": 2,
    "BLOCKED": 2,
    "SOURCE_BOUND": 3,
    "VERIFIED": 4,
    "VERIFIED_READ": 4,
    "VERIFIED_WRITE": 4,
    "VERIFIED_READ_WRITE": 5,
}

TRANSIENT_BLOCKERS = {
    "quota",
    "rate_limit",
    "account_disambiguation",
    "interactive_confirmation",
    "auth_expired",
    "project_binding",
    "provider_write_gate",
    "upstream_block",
}


class WorkerPolicy:
    """Deterministic rules that prevent churn, overclaiming, and unsafe repair."""

    @staticmethod
    def evidence_rank(state: str) -> int:
        return EVIDENCE_RANK.get(str(state).upper(), -1)

    @classmethod
    def reconcile_evidence(cls, prior_state: str, incoming_state: str) -> str:
        """Do not let a weaker stale projection demote stronger evidence."""
        if cls.evidence_rank(incoming_state) >= cls.evidence_rank(prior_state):
            return incoming_state
        return prior_state

    @staticmethod
    def should_probe_verified_core(
        evidence_state: str,
        regression_signal: bool = False,
        explicit_recheck: bool = False,
    ) -> bool:
        verified = str(evidence_state).upper().startswith("VERIFIED")
        if not verified:
            return True
        return bool(regression_signal or explicit_recheck)

    @staticmethod
    def should_retry_same_route(
        blocker_kind: str,
        materially_different_route: bool = False,
        provider_state_changed: bool = False,
    ) -> bool:
        if materially_different_route or provider_state_changed:
            return True
        return str(blocker_kind).lower() not in TRANSIENT_BLOCKERS

    @staticmethod
    def account_binding_decision(
        candidate_count: int,
        explicit_binding: bool,
    ) -> Dict[str, Any]:
        if explicit_binding:
            return {"runnable": True, "state": "BOUND"}
        if candidate_count > 1:
            return {
                "runnable": False,
                "state": "BLOCKED_ACCOUNT_DISAMBIGUATION",
                "reason": "multiple_provider_accounts_without_explicit_binding",
            }
        return {"runnable": True, "state": "SINGLE_CANDIDATE"}

    @staticmethod
    def can_promote_write(
        provider_accepted: bool,
        provider_readback: bool,
        exercised_surface: Optional[str],
    ) -> Dict[str, Any]:
        verified = bool(
            provider_accepted and provider_readback and exercised_surface
        )
        return {
            "verified": verified,
            "state": "VERIFIED_WRITE" if verified else "UNVERIFIED",
            "scope": exercised_surface if verified else None,
            "reason": (
                None
                if verified
                else "write_requires_acceptance_readback_and_scope"
            ),
        }

    @staticmethod
    def security_mutation_gate(
        current_state_read: bool,
        legitimate_access_paths_recovered: bool,
        intended_roles_explicit: bool,
        post_mutation_readback_planned: bool,
    ) -> Dict[str, Any]:
        checks = {
            "current_state_read": bool(current_state_read),
            "legitimate_access_paths_recovered": bool(
                legitimate_access_paths_recovered
            ),
            "intended_roles_explicit": bool(intended_roles_explicit),
            "post_mutation_readback_planned": bool(
                post_mutation_readback_planned
            ),
        }
        missing = [
            name for name, passed in checks.items() if not passed
        ]
        return {
            "runnable": not missing,
            "state": (
                "READY"
                if not missing
                else "BLOCKED_SECURITY_PRECONDITION"
            ),
            "missing": missing,
        }

    @staticmethod
    def deployment_repair_gate(
        failed_commit_is_current: bool,
        source_comparison_completed: bool,
    ) -> Dict[str, Any]:
        if not source_comparison_completed:
            return {
                "runnable": False,
                "state": "BLOCKED_PENDING_SOURCE_COMPARISON",
            }
        if not failed_commit_is_current:
            return {
                "runnable": False,
                "state": "STALE_FAILURE_DO_NOT_REPAIR_CURRENT_SOURCE",
            }
        return {
            "runnable": True,
            "state": "CURRENT_FAILURE_REPAIRABLE",
        }

    @classmethod
    def authority_aware_reconcile(
        cls,
        prior: Dict[str, Any],
        incoming: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Preserve claims from distinct authority domains instead of collapsing them."""
        prior_authority = str(prior.get("authority", "UNKNOWN"))
        incoming_authority = str(incoming.get("authority", "UNKNOWN"))
        incoming_value = incoming.get("value")
        incoming_rank = cls.evidence_rank(
            str(incoming.get("evidence", "UNVERIFIED"))
        )
        prior_rank = cls.evidence_rank(
            str(prior.get("evidence", "UNVERIFIED"))
        )

        if prior_authority != incoming_authority:
            if incoming_value is None or incoming_rank < prior_rank:
                return {
                    "state": "PRESERVE_DISTINCT_AUTHORITY",
                    "selected": dict(prior),
                    "preserved": [dict(prior), dict(incoming)],
                    "reason": (
                        "different_authority_domain_does_not_demote_prior_claim"
                    ),
                }
            return {
                "state": "PRESERVE_DISTINCT_AUTHORITY",
                "selected": None,
                "preserved": [dict(prior), dict(incoming)],
                "reason": "different_authority_domains_are_not_collapsed",
            }

        selected = dict(
            incoming if incoming_rank >= prior_rank else prior
        )
        return {
            "state": "RECONCILED_SAME_AUTHORITY",
            "selected": selected,
            "preserved": [dict(prior), dict(incoming)],
        }

    @staticmethod
    def interpret_negative_result(
        query_completed: bool,
        source_complete: bool,
        matches: int,
    ) -> Dict[str, Any]:
        """Missing retrieval and partial coverage are never promoted to absence."""
        if not query_completed:
            return {
                "state": "RETRIEVAL_GAP",
                "proves_absence": False,
                "matches": matches,
            }
        if matches > 0:
            return {
                "state": "MATCH_FOUND",
                "proves_absence": False,
                "matches": matches,
            }
        if not source_complete:
            return {
                "state": "NO_MATCH_IN_PARTIAL_COVERAGE",
                "proves_absence": False,
                "matches": 0,
            }
        return {
            "state": "ABSENCE_SUPPORTED_WITHIN_COMPLETE_SOURCE",
            "proves_absence": True,
            "matches": 0,
        }

    @staticmethod
    def fallback_gate(
        required_capabilities: Any,
        fallback_capabilities: Any,
    ) -> Dict[str, Any]:
        """Classify fallback loss instead of silently treating substitutes as equal."""
        required = set(required_capabilities)
        fallback = set(fallback_capabilities)
        lost = sorted(required - fallback)
        return {
            "equivalent": not lost,
            "state": (
                "EQUIVALENT_FALLBACK"
                if not lost
                else "DEGRADED_FALLBACK"
            ),
            "lost_capabilities": lost,
        }

    @staticmethod
    def projection_loss_gate(
        source_fields: Any,
        projected_fields: Any,
        protected_fields: Any,
    ) -> Dict[str, Any]:
        """Prevent projections from silently dropping authority/provenance semantics."""
        source = set(source_fields)
        projected = set(projected_fields)
        protected = set(protected_fields)
        lost = sorted((source - projected) & protected)
        return {
            "runnable": not lost,
            "state": (
                "LOSSLESS_PROJECTION"
                if not lost
                else "BLOCKED_HIDDEN_HARM_PROJECTION_LOSS"
            ),
            "lost_protected_fields": lost,
        }

    @staticmethod
    def mutation_reversibility_gate(
        reversible_surface: bool,
        pre_state_captured: bool,
        rollback_route_known: bool,
        idempotency_key_present: bool,
    ) -> Dict[str, Any]:
        """Require recovery information before reversible connector mutations."""
        checks = {
            "pre_state_captured": bool(pre_state_captured),
            "rollback_route_known": bool(rollback_route_known),
            "idempotency_key_present": bool(idempotency_key_present),
        }
        missing = (
            [name for name, passed in checks.items() if not passed]
            if reversible_surface
            else []
        )
        return {
            "runnable": not missing,
            "state": (
                "READY"
                if not missing
                else "BLOCKED_HIDDEN_HARM_IRREVERSIBLE_WRITE"
            ),
            "missing": missing,
        }

    @staticmethod
    def privacy_projection_gate(
        source_boundary: str,
        target_boundary: str,
        explicit_declassification: bool = False,
    ) -> Dict[str, Any]:
        """Prevent private/restricted material from silently widening visibility."""
        rank = {
            "PUBLIC": 0,
            "INTERNAL": 1,
            "PRIVATE": 2,
            "RESTRICTED": 3,
        }
        source = str(source_boundary).upper()
        target = str(target_boundary).upper()
        source_rank = rank.get(source, 3)
        target_rank = rank.get(target, 3)
        widening = target_rank < source_rank
        if widening and not explicit_declassification:
            return {
                "runnable": False,
                "state": "BLOCKED_HIDDEN_HARM_PRIVACY_WIDENING",
                "source_boundary": source,
                "target_boundary": target,
            }
        return {
            "runnable": True,
            "state": "PRIVACY_BOUNDARY_PRESERVED",
            "source_boundary": source,
            "target_boundary": target,
        }

    @classmethod
    def demotion_gate(
        cls,
        current_state: str,
        proposed_state: str,
        disconfirming_provider_evidence: bool,
        provider_scope_changed: bool,
    ) -> Dict[str, Any]:
        """A missing/weaker observation cannot silently demote stronger state."""
        is_demotion = (
            cls.evidence_rank(proposed_state)
            < cls.evidence_rank(current_state)
        )
        if not is_demotion:
            return {"allowed": True, "state": "NO_DEMOTION"}
        if provider_scope_changed:
            return {
                "allowed": False,
                "state": "SCOPE_SPLIT_REQUIRED",
                "reason": (
                    "new_scope_must_not_demote_previous_verified_scope"
                ),
            }
        if not disconfirming_provider_evidence:
            return {
                "allowed": False,
                "state": "BLOCKED_HIDDEN_HARM_DEMOTION",
                "reason": (
                    "missing_or_weaker_evidence_cannot_demote_stronger_state"
                ),
            }
        return {
            "allowed": True,
            "state": "DEMOTION_SUPPORTED_BY_PROVIDER_EVIDENCE",
        }

    @staticmethod
    def material_delta(
        newly_verified: bool = False,
        seam_repaired: bool = False,
        coalition_strengthened: bool = False,
    ) -> bool:
        return bool(
            newly_verified or seam_repaired or coalition_strengthened
        )
