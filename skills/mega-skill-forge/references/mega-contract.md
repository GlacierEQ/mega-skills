# Mega Skill Contract

A Mega Skill is an orchestration layer above Combo Skills. It must not replay their procedures. Its contract must state: mission; selection and non-selection; required Combos; conditional Combos; readiness route; route algorithm; compound output; durable state; evidence integration; approval boundary; recovery rule; and the incremental integration value.

Every selected Combo must be registered and its compound artifact must appear as a named Mega input. Require `long-horizon-core` when the work spans dependent phases or needs recovery. Add `capability-readiness` as a conditional route whenever an advanced capability could depend on unverified prerequisites or make a strong claim.

Use precise language. “Coordinates,” “records,” “gates,” and “routes” describe orchestration. Do not say “executes,” “guarantees,” “certifies,” or “autonomously performs” when the contract has not observed the required resources, approvals, and evidence.
