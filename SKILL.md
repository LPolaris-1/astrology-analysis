---
name: astrology-analysis
description: Compute and deeply interpret a Western tropical natal chart (本命盘 / 星盘 / birth chart) from birth date, exact time, and location. Use for planetary positions, signs, houses, rulership chains, aspects, chart patterns, personality, career, and relationships. Do not use for Vedic/sidereal astrology, Chinese astrology, tarot, horary, electional, daily horoscopes, or astronomy-only questions.
---

# Western Natal Astrology

Use deterministic astronomy for the chart and interpret only the resulting canonical data. Never calculate placements from memory or let biography rewrite the chart.

## Scope and defaults

- Reading type: natal only.
- Zodiac: tropical.
- House system: Placidus by default; Whole Sign when requested.
- Bodies: Sun through Pluto plus True Node; angles when birth time is known.
- Aspects: conjunction, opposition, trine, square, sextile; use the calculator's applying/separating state and orbs.
- Interpretation mode: blended classical and modern unless the user asks for one tradition.

Keep Western and Vedic rules separate. Astrology is an interpretive tradition, not demonstrated scientific causation. Use tendencies and conditions, not fate claims.

## Required input

Collect or normalize:

- birth date;
- local clock time and its source/precision;
- birthplace label, latitude, longitude, and IANA timezone;
- optional preferred house system and interpretation focus.

Do not infer a timezone from longitude. If a place or historical timezone is uncertain, verify it before calculating. If birth time is unknown, explicitly use unknown-time mode: omit Ascendant, Midheaven, houses, sect, angularity, and house-ruler conclusions; mark the Moon provisional where needed.

## Deterministic calculation

Before the first chart in a new environment or after changing scripts/ephemeris data, run:

```bash
python -X utf8 scripts/self_test.py
```

The test must pass and report `Swiss Ephemeris .se1`. A missing `.se1` file, Moshier fallback, failed invariant, or precision mismatch is a stop condition, not a warning to ignore.

Create an input JSON following [calculation-and-validation.md](references/calculation-and-validation.md), then run:

```bash
python -X utf8 scripts/natal_pipeline.py --input input.json --output chart_data.json
```

Proceed only when `validation.status` is `passed`. Treat `chart_data.json` as the single source of truth. The analysis layer must not recalculate signs, houses, dignity, aspects, or applying/separating state.

## Input-stability gate

Use the uncertainty interval justified by the time source, not a convenient default. The pipeline resamples the chart across that interval.

- `stable`: the factor may be used normally.
- `boundary_sensitive`: present alternatives or downgrade the conclusion.
- `not_audited`: do not present the factor as certain.
- `not_applicable`: the birth time is unknown and time-dependent factors are unavailable.

Mathematical reproducibility does not prove that the recorded birth time is exact.

## Deep analysis workflow

Read [analysis-workflow.md](references/analysis-workflow.md). Work in two phases:

1. **Blind chart audit** — use only `chart_data.json`; do not read biography or prior feedback. Identify dominant signatures, contradictions, dispositor/rulership chains, angularity, sect/condition, and aspect networks. Build an internal evidence matrix before prose.
2. **User-facing synthesis** — after the blind audit is fixed, confirmed facts may test or illustrate a conclusion. The direction must remain `chart -> possible manifestation -> user confirmation`, never `biography -> retrofitted chart meaning`.

Load only relevant references using [resource-map.md](references/resource-map.md). Do not read the entire library by default. Generic planet, sign, and house meanings are ingredients, not finished conclusions.

Weight evidence roughly in this order:

1. repeated independent signatures and chart ruler;
2. Sun, Moon, Ascendant, MC, angular planets, and rulers of the relevant houses;
3. tight aspects and coherent aspect networks;
4. sect, major essential dignity/debility, retrogradation, combustion, and house condition;
5. isolated weak or wide-orb symbolism.

Do not average contradictions into vague language. State what each side governs, the conditions under which it appears, and which evidence is stronger.

## Output contract

Read [output-and-corrections.md](references/output-and-corrections.md). Do not dump raw JSON. Match the deliverable to the request:

- **Focused answer** — answer the requested theme directly and include only the evidence needed to support it.
- **Complete reading** — default to a structured Markdown report in the user's language.
- **Browser report** — when the user requests HTML, a browser view, or a formally packaged complete report, generate a self-contained responsive HTML file with navigation, printable styling, and a technical appendix.

Put **audit scope and boundaries** at the beginning once: calculation basis, audited time interval, included factors, excluded factors, validation status, and the five separate confidence dimensions. Do not repeat generic disclaimers in every section; keep only claim-specific limitations beside the claim they affect.

For a complete reading, organize the report in this order:

1. audit scope, boundaries, and confidence;
2. concise chart thesis and executive summary;
3. whole-chart architecture: chart ruler, dominant configurations, aspect networks, dispositors, sect, element/modality, and primary stabilizers/tensions;
4. personality and emotional regulation;
5. thinking, communication, and learning;
6. action, conflict, boundaries, and recovery;
7. home, family, and private foundations;
8. creativity, interests, community, and friendship;
9. career, work systems, and public role;
10. money, personal resources, shared resources, and risk;
11. relationships, intimacy, trust, and repair;
12. solitude, unconscious patterns, rest, and spirituality;
13. house-axis synthesis and planet-by-planet role audit when useful;
14. strengths, risks, prioritized actions, and technical appendix.

Merge repeated signals instead of restating the same placement in multiple sections. Expand or compress domains according to evidence; completeness means every materially supported life area is checked, not that every planet or house receives equal space.

For every major claim make this chain explicit: **conclusion -> chart evidence -> constraint/counter-evidence -> possible manifestations -> practical implication**. Lead with plain language and place technical details after it. Use natural, specific language; do not disguise inference as fact.

For formatted reports, follow the sample-and-verify workflow in [output-and-corrections.md](references/output-and-corrections.md). Do not stop after producing a file: render it, inspect the actual layout, and verify desktop and narrow-screen readability before delivery.

## Corrections

Never silently overwrite an earlier interpretation.

- Feedback about lived experience updates the correction log; preserve the original claim and score.
- Classify the miss as input/calculation, domain, manifestation, or weighting error.
- If birth facts change, create a new version of `chart_data.json` and rerun the full calculation; do not patch placements by hand.
- User feedback may refine expression but may not change deterministic chart data.

## Safety and epistemic limits

- Do not predict death, severe illness, catastrophe, or legal outcomes.
- Do not give medical, legal, or financial decisions as astrological conclusions.
- Avoid diagnosis, fatalism, fear-based language, and universal Barnum statements.
- If the user is in crisis, respond to the person first and set astrology aside.
- Distinguish astronomical calculation confidence from interpretive confidence and external validation.
