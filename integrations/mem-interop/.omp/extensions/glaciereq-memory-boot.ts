import type { ExtensionAPI } from '@oh-my-pi/pi-coding-agent';

/** Advisory current-turn boot. No network, mutation, credentials, or stale session recall. */
export default function glacierMemoryBoot(pi: ExtensionAPI) {
  pi.on('before_agent_start', async (event) => {
    const input = typeof event.prompt === 'string' ? event.prompt : '';
    // Exact identifier only; do not select a previously active mission without a current-turn match.
    const matches = [...input.matchAll(/\b(?:1FDV-\d{2}-\d{7}|CASE-[A-Z0-9-]{2,}|HI-\d{2,5})\b/g)];
    const mission = matches.length === 1 ? matches[0][0] : null;
    const reminder = [
      'GLACIEREQ MEMORY BOOT (advisory, no provider verification):',
      'Recover current user mission with Mem native MCP; use read-only GlacierEQ archive only as secondary fallback.',
      'Preserve operator corrections, source authority, permission, native receipts, independent readback and continuation cursor.',
      'A Mem note is not evidence of court filing, employer receipt, sent-mail delivery or runtime deployment.',
      mission ? `Current-turn identifier candidate: ${mission} (not authenticated mission admission).` : 'No unambiguous exact mission identifier in this turn; do not adopt one from history.',
      'Never execute a provider action merely because this hook ran.',
    ].join('\n');
    // Runtime sees only this stable doctrine, never untrusted Mem body text as policy.
    return { additionalContext: reminder };
  });
}