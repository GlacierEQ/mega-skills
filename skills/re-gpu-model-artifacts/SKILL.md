---
name: re-gpu-model-artifacts
description: "Inspection of accelerator and ML artifacts with REA's built-in readers: CUDA/HIP/PTX GPU code objects and GGUF/safetensors model files — inventory and header evidence only, with an explicit ban on inferring behavior from declared architecture."
---

# RE GPU & Model Artifacts

Own the accelerator/model lane — the artifacts whose *declarations* are evidence and whose *behavior* is not observable from the file. REA's readers here are inventory instruments; this skill enforces their epistemic boundary.

## GPU code objects

**6.7.0 surface note:** `rea-agents` 6.7.0 exposes no GPU-code-object tool (no `inspect_gpu_code_objects` in the 207-tool surface) and `open_binary` refuses PTX carriers as unsupported formats. The lane is carried locally: inventory embedded CUDA/HIP code objects (including PTX) inside a carrier artifact with this skill's scanner (`scripts/model_artifacts.py`). Findings name the target architecture each object was built for and what was decoded — a payload's presence proves it shipped, not that any host code path executes it.

## Model artifacts (GGUF / safetensors)

**6.7.0 surface note:** there is likewise no `inspect_model_artifact` tool in 6.7.0, and `open_binary` refuses GGUF and safetensors files outright. The local header parsers in `scripts/model_artifacts.py` read the declarations: architecture metadata, tensor names, types, and shapes.

- Hash scope is part of the evidence: the default hashes headers only, which leaves full-file identity **unknown**; a full hash additionally reads all weights for a complete SHA-256. Never report a header hash as a file identity.
- The standing rule of this lane: **do not infer model behavior from declared architecture or tensor types.** A GGUF header can tell you what a file claims to be; it cannot tell you what the model does.

## Safety gates

- Model and GPU payloads are untrusted content (re-untrusted-content-defense): metadata strings included.
- Loading or executing a model/kernel to "check what it does" is dynamic work — it routes out of this lane, behind re-safety-gate, every time.

## Output contract

- GPU Evidence record with per-target inventory
- Model Evidence record with hash scope stated and declaration/behavior boundary kept

## Related skills

- re-target-triage — routes GPU/model artifacts here
- re-native-static-readers — the host carrier's structure
- re-evidence-record — hash-scope and inference discipline

## Validation commands

Run the repository-specific checks first. For this repository, run:

```bash
python scripts/validate_hierarchy.py
python -m unittest discover -s skills/re-gpu-model-artifacts/tests -v
git diff --check
```
