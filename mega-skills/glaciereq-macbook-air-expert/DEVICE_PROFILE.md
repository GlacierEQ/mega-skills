# Device Profile — KcBs-MacBook-Air.local

**Captured:** 2026-09-30 · **Model:** `MacBookAir7,2` · **macOS:** 14.8.7 (23J520)

All values below are **observations**, not specifications from memory. Re-run the preflight
before relying on this file; this host's configuration changes on its own (patch agents run at
load, and disk pressure fluctuates hourly).

## Preconditions gate (run first, every mission)

```sh
uptime                                    # load vs 4 threads; > 80 = remediate
vm_stat | head -6                          # pages free; < 10% = remediate
sysctl vm.swapusage                        # swap used; near-total = remediate
df -h /System/Volumes/Data                 # free space; < 10% = remediate
df -i /System/Volumes/Data                 # free inodes; < 10% = remediate
```

**Remediate before working if any gate fails.** On a starved host every measurement is
unreliable, and diagnostic tooling itself becomes the load. Do not run `du -sh -d 1 ~/Library`
or unbounded `find` to investigate — those are what drove this host to 100% disk and 77%
inode consumption.

## Hardware

| Property | Value | Command |
|---|---|---|
| Model | MacBookAir7,2 | `sysctl -n hw.model` |
| CPU | i5-5250U @ 1.60GHz, dual-core, 4 threads | `sysctl -n machdep.cpu.brand_string hw.ncpu` |
| RAM | 8 GB | `sysctl -n hw.memsize` |
| ISA | AVX1.0, SSE4.2, AES, F16C — **no AVX2** | `sysctl -n machdep.cpu.features` |
| GPU | Intel HD 6000, 1536 MB dynamic | `system_profiler SPDisplaysDataType` |
| Display | 1440x900 LCD | `system_profiler SPDisplaysDataType` |
| Internal disk | 121 GB APFS SSD | `system_profiler SPStorageDataType` |
| Battery | 338 cycles, Service Recommended | `system_profiler SPPowerDataType` |
| Serial | C02S953CH3QD | `system_profiler SPHardwareDataType` |

## OpenCore / OCLP

| Property | Value |
|---|---|
| OCLP version | 2.5.1 |
| OCLP path | `/Library/Application Support/Dortania/OpenCore-Patcher.app` |
| Auto-patch agent | `com.dortania.opencore-legacy-patcher.auto-patch` (RunAtLoad) |
| Update monitor | `com.dortania.opencore-legacy-patcher.macos-update` |
| RSR monitor | `com.dortania.opencore-legacy-patcher.rsr-monitor` |
| `boot-args` | `keepsyms=1 debug=0x100 -lilubetaall ipc_control_port_options=0 -nokcmismatchpanic` |
| macOS volume | 14.8.7 Sonoma, patched to run on 2015 hardware |

`auto-patch` runs at load with `RunAtLoad`, so patch state can change **without anyone
touching the machine**. Always verify actual state before diagnosing symptoms.

## Security posture

| Control | State | Check command |
|---|---|---|
| SIP | Custom config (Apple Internal, Kext Signing, Filesystem Protections disabled) | `csrutil status` |
| Authenticated Root | disabled | `csrutil authenticated-root status` |
| FileVault | Off | `fdesetup status` |
| Application firewall | Disabled (State = 0) | `/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate` |
| Gatekeeper | assessments enabled | `spctl --status` |
| `csr-active-config` | `%03%08%00%00` | `nvram csr-active-config` |
| Time Machine | **No destination configured** | `tmutil destinationinfo` |

Apple's own wording on this SIP state: *"This is an unsupported configuration, likely to break
in the future and leave your machine in an unknown state."* Record that in any report.

**No Time Machine destination + FileVault off + degraded battery = no tested restore path.**
This blocks all EFI/OpenCore work until backup is established.

## AI and toolchain

| Component | Value |
|---|---|
| Ollama | `/usr/local/bin/ollama`, serving on `*:11434` (all interfaces) |
| Local models | 13 registered (see `ollama list`) |
| `~/.ollama` size | reported 0 B — **inconsistent with 13 models; unverified** |
| LM Studio | not installed |
| Node | v26.7.0 |
| Python | 3.14.7 |
| uv | 0.12.5 |
| cargo | 1.98.0 |
| Go | not installed |

**Capability ceiling:** dual-core 2015 CPU, 8 GB RAM, no AVX2, no Apple Silicon. Local
inference is limited to small quantized models. The toolchain is for orchestration; the host is
not a training or high-throughput inference target.

## Off-prem surface

| Component | State |
|---|---|
| LAN address | 192.168.68.129/24 (en0) |
| Cloudflare WARP | `/Applications/Cloudflare WARP.app` + `/usr/local/bin/cloudflared` |
| Tailscale | app installed; CLI not on PATH |
| Active tunnels | `utun0`, `utun1` |
| Non-loopback listeners observed | `ollama` *:11434, `rapportd` *:63121, `IPNExtension` *:54099, `ARDAgent` *:3283, DropboxFileProvider *:17500 (removed 2026-09-30) |

With the application firewall disabled, **every `*`-bound listener is LAN-reachable**.

## Cloud storage

`~/Dropbox` does not exist. Storage is File Provider based at
`~/Library/CloudStorage/Dropbox-Cyber.lazer.mermicor` (team account `Cyber.lazer.mermicor`,
business team, host 20794627395).

**Rule:** provider mounts are virtual. Deleting inside `~/Library/CloudStorage/*` propagates
deletion to the cloud and to every linked device. Never `rm` there.

## Known history (2026-09-30)

- Load peaked at **983** on 4 threads; free RAM fell to **0.25%**; swap auto-grew 4096M→5120M.
- A 144 MB `kilo` server failed a 30s startup timeout; the same binary started in ~3 minutes
  under reduced load. **Root cause was starvation, not the binary.**
- Disk reached **100% full with 1.3M free inodes**, then self-recovered to 92%.
- Dropbox was stopped and disabled (processes, launchd registration, 3 plists backed up to
  `~/dropbox-removal-backup/`). `Dropbox.app` (709M) and `~/.dropbox` (487M) remain on disk;
  ~660M of app cache was removed.
- A live Supabase `service_role` key was exposed in a LaunchAgent plist and printed to a
  transcript during that incident. **Rotate it.** That key bypasses RLS entirely.
- A `/tmp/rotate_monthly.sh` cron entry points at a file that no longer exists.
