---
id: interactive-media-3d-pipeline
display_name: Interactive Media 3D Pipeline
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Interactive Media 3D Pipeline

## Purpose and selection

WebGL 3D rendering, canvas algorithmic art, and generative UI previews are required.

## Incremental value

This Combo Skill composes canvas-design, algorithmic-art, generative-ui into a unified, verified `INTERACTIVE_SCENE_RECORD.md`.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `canvas-design` | skill | Yes | Define 2D/3D canvas layouts, viewports, and render buffers. | Canvas spec, Viewport parameters | canvas-scene-manifest.json | Canvas dimensions and context bind cleanly. |
| 2 | `algorithmic-art` | skill | Yes | Generate procedural shader mathematics and geometry transforms. | canvas-scene-manifest.json | shader-pipeline-bundle.json | Mathematical shader formulas evaluate without NaN. |
| 3 | `generative-ui` | skill | Yes | Compile live interactive UI prototypes and artifact carousels. | shader-pipeline-bundle.json | INTERACTIVE_SCENE_RECORD.md | Interactive UI renders at target frame rate. |

## Ordered execution

1. **canvas-design** consumes Canvas spec, Viewport parameters, produces canvas-scene-manifest.json, and verifies Canvas dimensions and context bind cleanly..
2. **algorithmic-art** consumes canvas-scene-manifest.json, produces shader-pipeline-bundle.json, and verifies Mathematical shader formulas evaluate without NaN..
3. **generative-ui** consumes shader-pipeline-bundle.json, produces INTERACTIVE_SCENE_RECORD.md, and verifies Interactive UI renders at target frame rate..

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `canvas-design` | `algorithmic-art` | canvas-scene-manifest.json | shader-pipeline-bundle.json | `canvas-design` | Verified handoff |
| `algorithmic-art` | `generative-ui` | shader-pipeline-bundle.json | INTERACTIVE_SCENE_RECORD.md | `algorithmic-art` | Verified handoff |

## Compound output

Produce `INTERACTIVE_SCENE_RECORD.md` upon completion.
