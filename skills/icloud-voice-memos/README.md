# iCloud Voice Memos Harvester

## What it does
Logs into iCloud.com via Chromium browser automation and extracts:
- **Transcripts** (Apple auto-generated)
- **GPS / location metadata**
- **Timestamps** (creation time, duration)
- **Title and memo ID**

Outputs structured JSON to `/tasklet/voice-memos/`.

## No app breach required
Pure browser automation against icloud.com. Credentials in `~/.apex/connections.json`.

## Setup
```json
// ~/.apex/connections.json
{
  "apple": {
    "apple_id": "your@apple.id",
    "password": "your_password"
  }
}
```

## Run
```bash
python skills/icloud-voice-memos/harvester.py
```

## Output format
```json
{
  "run_id": "20260624T070000Z",
  "count": 42,
  "memos": [
    {
      "title": "Court notes June 23",
      "duration": "3:47",
      "timestamp": "Jun 23, 2026",
      "transcript": "Meeting with attorney...",
      "memo_id": "abc123",
      "gps_raw": "21.3069° N, 157.8583° W",
      "harvested_at": "2026-06-24T07:00:00Z",
      "source": "icloud.com"
    }
  ]
}
```

*GlacierEQ APEX | June 2026*
