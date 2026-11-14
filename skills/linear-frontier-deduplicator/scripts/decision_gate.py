"""Pure, fail-closed action-admission decision helper.

No network, email sending, Linear writes, legal conclusions or authentication is
performed here. Caller must source original provider events and approvals.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping, Sequence

KNOWN_STAGES = frozenset({
    'DRAFT', 'SENT', 'RECEIVED', 'ACKNOWLEDGED', 'ASSIGNED', 'PROCESSING',
    'PARTIAL', 'PRODUCED', 'DENIED', 'APPEALED', 'AMBIGUOUS_SEND', 'WITHDRAWN', 'REMEDIED',
})
WAITING = frozenset({'SENT', 'RECEIVED', 'ACKNOWLEDGED', 'ASSIGNED', 'PROCESSING'})


def _result(decision: str, stage: str, reason: str) -> dict[str, object]:
    return {
        'decision': decision,
        'latest_stage': stage,
        'reason': reason,
        'outcome_verified': False,
        'external_effect_executed': False,
    }


def decide_correspondence(
    *, action_key: str, expected_sender: str, authenticated_sender: str,
    approved: bool, events: Sequence[Mapping[str, object]],
    coverage_verified: bool = False,
) -> dict[str, object]:
    """Choose a safe next *classification*, never execute external effects.

    action_key must combine beneficiary, case, custodian, intended effect and
    stable provider-thread identity where known. The caller must fetch events
    from ALL relevant mailboxes and provider sources before using this result.
    """
    if not all(isinstance(v, str) and v.strip() for v in (action_key, expected_sender, authenticated_sender)):
        return _result('BLOCK_IDENTITY_UNRESOLVED', 'UNKNOWN', 'Mission, sender or connected-account identity unavailable')
    if expected_sender.strip().casefold() != authenticated_sender.strip().casefold():
        return _result('BLOCK_WRONG_SENDER', 'UNKNOWN', 'Authenticated mailbox does not match expected first-party sender')

    if not coverage_verified:
        return _result('NEEDS_SOURCE_COVERAGE', 'UNKNOWN', 'Relevant accounts, complete threads and owning action graph have not been verified')

    relevant = [e for e in events if e.get('action_key') == action_key]
    for e in relevant:
        if e.get('stage') not in KNOWN_STAGES:
            return _result('NEEDS_PROOF', 'UNKNOWN', 'Unrecognized or missing provider stage')

    if not relevant:
        return _result('READY_FOR_DISPATCH' if approved else 'DRAFT_ONLY',
                       'NONE', 'No existing action event found in verified source scope; pre-dispatch recheck and reservation still required')

    try:
        normalized = []
        for event in relevant:
            instant = datetime.fromisoformat(str(event.get('observed_at', '')).replace('Z', '+00:00'))
            if instant.tzinfo is None:
                raise ValueError('Offset required')
            normalized.append((instant.astimezone(timezone.utc), event))
        normalized.sort(key=lambda pair: pair[0])
    except (TypeError, ValueError, OverflowError):
        return _result('NEEDS_PROOF', 'UNKNOWN', 'Provider event timestamp invalid or timezone missing')
    for left, right in zip(normalized, normalized[1:]):
        if left[0] == right[0] and left[1]['stage'] != right[1]['stage']:
            return _result('NEEDS_PROOF', 'UNKNOWN', 'Contradictory stages share an observed instant')
    relevant = [event for _, event in normalized]
    ambiguous = [e for e in relevant if e['stage'] == 'AMBIGUOUS_SEND']
    if ambiguous and relevant[-1]['stage'] != 'AMBIGUOUS_SEND':
        latest_ambiguous = max(
            datetime.fromisoformat(str(e['observed_at']).replace('Z', '+00:00')).astimezone(timezone.utc)
            for e in ambiguous
        )
        if not any(t > latest_ambiguous and e.get('resolution_verified') is True for t, e in normalized):
            return _result('NEEDS_PROOF', 'AMBIGUOUS_SEND', 'Ambiguous delivery lacks independent resolution proof')

    stage = str(relevant[-1]['stage'])
    # A later unsent draft cannot undo a prior effect for the same action key.
    # A distinct appeal or follow-up must use a distinct action identity.
    if stage == 'DRAFT':
        for prior in reversed(relevant[:-1]):
            if prior['stage'] != 'DRAFT':
                stage = str(prior['stage'])
                break
    if stage == 'AMBIGUOUS_SEND':
        return _result('NEEDS_PROOF', stage, 'Unknown delivery must be read back before retry')
    if stage in WAITING:
        return _result('WAITING_EXTERNAL', stage, 'An outbound request already exists; do not replay')
    if stage == 'APPEALED':
        return _result('WAITING_APPEAL', stage, 'An appeal is already pending; verify its disposition before another appeal')
    if stage == 'PARTIAL':
        return _result('RECONCILE_PARTIAL', stage, 'Reconcile received and unfulfilled categories before further contact')
    if stage == 'PRODUCED':
        return _result('VERIFY_PRODUCTION', stage, 'Audit native production; source receipt alone does not prove remedy')
    if stage == 'DENIED':
        return _result('REVIEW_ADVERSE_DETERMINATION', stage, 'Preserve actual written denial and check applicable review path')
    if stage == 'REMEDIED':
        return _result('VERIFY_REMEDY', stage, 'Independently test requested real-world outcome before mission closure')
    if stage == 'WITHDRAWN':
        return _result('REASSESS_AUTHORIZATION', stage, 'Prior action withdrawn; fresh consent and cause required')
    return _result('READY_FOR_DISPATCH' if approved else 'DRAFT_ONLY',
                   stage, 'Draft is not sent; authorization and pre-dispatch provider recheck required')
