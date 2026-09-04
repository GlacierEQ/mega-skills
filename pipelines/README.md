# Pipelines

Executable DAGs for GlacierEQ Mega Skills.

| File | Family | Span |
|---|---|---|
| `inception-to-deployment.json` | master | inception → evolve |
| `control-plane.json` | control-plane | inception → evolve |
| `memory-fleet.json` | memory-fleet | inception → evolve |
| `change-swe.json` | change-swe | inception → evolve |
| `ship-cloud.json` | ship-cloud | inception → evolve |
| `anthropic-applied-ai-readiness.json` | mission | career evidence only |

Schema: `schemas/pipeline.schema.json`  
Registry: `registry/pipelines.json`  
Engine: `skills/pipeline-compositor/scripts/engine.py`  
Stages: `scripts/deep_work_stage.py`

Do not add a stage that performs deploy, merge, network send, or credential
access. The ship family stops at an approval packet.
