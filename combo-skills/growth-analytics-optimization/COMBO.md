---
id: growth-analytics-optimization
display_name: Growth Analytics Optimization
schema: ../../schemas/combo-skill.schema.json
version: 0.1.0
status: active
---

# Growth Analytics Optimization

## Purpose and selection

Growth funnel optimization, competitive intelligence extraction, and A/B test analytics are needed.

## Incremental value

This Combo Skill composes competitive-ads-extractor, ab-test-setup, analytics-tracking into a unified, verified `GROWTH_EXPERIMENT_RECORD.md`.

## Member contract

| Order | Member ID | Kind | Required | Role in this Combo | Receives | Must produce | Local validation |
|---:|---|---|---|---|---|---|---|
| 1 | `competitive-ads-extractor` | skill | Yes | Extract competitive positioning, ad hooks, and audience signals. | Market positioning, Competitor URLs | competitive-intel-summary.json | Signals extracted with confidence scores. |
| 2 | `ab-test-setup` | skill | Yes | Configure statistical A/B test hypotheses, sample size, and variants. | competitive-intel-summary.json | ab-test-variant-manifest.json | Sample size power calculation reaches 80%+ statistical power. |
| 3 | `analytics-tracking` | skill | Yes | Instrument event telemetry, conversion funnels, and statistical reporting. | ab-test-variant-manifest.json | GROWTH_EXPERIMENT_RECORD.md | Telemetry pipelines capture conversion funnel events. |

## Ordered execution

1. **competitive-ads-extractor** consumes Market positioning, Competitor URLs, produces competitive-intel-summary.json, and verifies Signals extracted with confidence scores..
2. **ab-test-setup** consumes competitive-intel-summary.json, produces ab-test-variant-manifest.json, and verifies Sample size power calculation reaches 80%+ statistical power..
3. **analytics-tracking** consumes ab-test-variant-manifest.json, produces GROWTH_EXPERIMENT_RECORD.md, and verifies Telemetry pipelines capture conversion funnel events..

## Handoff contracts

| From | To | Required inputs | Accepted output | Failure owner | Close condition |
|---|---|---|---|---|---|
| `competitive-ads-extractor` | `ab-test-setup` | competitive-intel-summary.json | ab-test-variant-manifest.json | `competitive-ads-extractor` | Verified handoff |
| `ab-test-setup` | `analytics-tracking` | ab-test-variant-manifest.json | GROWTH_EXPERIMENT_RECORD.md | `ab-test-setup` | Verified handoff |

## Compound output

Produce `GROWTH_EXPERIMENT_RECORD.md` upon completion.
