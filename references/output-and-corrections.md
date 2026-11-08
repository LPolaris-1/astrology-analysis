# Output and correction contract

## Five confidence dimensions

Do not collapse confidence into one label.

1. **Calculation confidence** — engine, ephemeris files, invariants, fixture test.
2. **Input stability** — sensitivity to the justified birth-time interval.
3. **Structural convergence** — whether independent chart factors point to the same theme.
4. **Interpretation confidence** — strength and specificity of the doctrine-to-language mapping.
5. **External validation** — not validated, user-confirmed, contradicted, or mixed.

Calculation success does not automatically increase interpretation or external-validation confidence.

## Report structure

```markdown
# Western Natal Chart Reading

## Audit scope and boundaries
## Executive summary and chart thesis
## Whole-chart architecture
## Personality and emotional regulation
## Thinking, communication, and learning
## Action, conflict, boundaries, and recovery
## Home, family, and private foundations
## Creativity, interests, friendship, and community
## Career, work systems, and public role
## Money, personal resources, shared resources, and risk
## Relationships, intimacy, trust, and repair
## Solitude, unconscious patterns, rest, and spirituality
## House-axis synthesis
## Planet-by-planet role audit
## Strengths, risks, and prioritized actions
## Technical appendix
### Placements and houses
### Major aspects
### Evidence matrix
### Calculation and stability audit
### Correction log
```

Use prose for synthesis and tables for exact mappings. The main body should be roughly 70% plain-language interpretation, 20% evidence, and 10% technical caveats. This is a balance, not a word-count quota. Compress or combine headings when evidence is thin; do not invent material to preserve the template.

The opening scope block must centralize:

- calculation engine, zodiac, house system, place, timezone, and time source;
- audited uncertainty interval and stability result;
- included bodies, points, aspects, and interpretive traditions;
- excluded techniques and questions;
- validation status and five confidence dimensions;
- external-validation status.

Do not repeat these general boundaries throughout the report. Keep a local limitation only when it changes a specific conclusion.

## Formatted and browser deliverables

Use Markdown for ordinary readings. When the user requests HTML, a browser view, or a formal complete report:

1. Create a small representative sample containing the title, scope block, confidence display, one evidence-led claim, and one table.
2. Render the sample in the requested browser when available, otherwise in a compatible Chromium engine. Inspect Chinese text, hierarchy, colors, navigation, table behavior, and print contrast.
3. Continue to the full report without waiting when no material preference is missing and the user did not request sample approval.
4. Generate one self-contained HTML file: local CSS, semantic headings, section anchors, responsive navigation, printable styling, and no external asset dependency unless explicitly authorized.
5. Render the complete report at a desktop viewport and a narrow viewport. Verify that headings, cards, tables, and navigation do not overlap or escape the page.
6. Check document integrity: expected section count, unique IDs, valid closing structure, no unintended duplicate report, and no horizontal overflow outside intentionally scrollable tables.
7. Deliver the HTML path first. List preview images and sample files separately as temporary verification artifacts; do not delete them without authorization.

A successful file write is not acceptance. Acceptance requires rendered visual inspection plus the structural checks above.

## Claim format

Each major claim should make these traceable:

- conclusion;
- chart evidence;
- constraint or counter-evidence;
- plausible range of manifestations;
- practical implication;
- structural and interpretive confidence.

Prefer this compact order in prose:

1. **Conclusion** — the lived pattern in plain language.
2. **Chart evidence** — exact placements, rulers, aspects, or repeated networks.
3. **Constraint / counter-evidence** — what narrows or modifies the claim.
4. **Possible manifestations** — two or three concrete expressions, identifying the primary form when justified.
5. **Practical implication** — a specific decision rule, boundary, habit, or experiment.

For long reports, use these labels only where they improve traceability. Natural prose is acceptable when all five parts remain clear.

## Correction log

Never delete or silently rewrite the original claim. Append:

| Field | Content |
|---|---|
| Original claim | Exact short claim or stable identifier |
| Original evidence | Placements/aspects/rulers used |
| Original confidence | Structural / interpretation / external status |
| User feedback | Confirmed, contradicted, mixed, or unclear |
| Error axis | input-calculation / domain / manifestation / weighting |
| Revised interpretation | What changes and what remains |
| Recalculation required | yes/no and why |

Feedback may validate or refine an interpretation, but it may not alter astronomical data. A changed date, time, timezone, latitude, longitude, zodiac, or house system requires a new canonical chart version.

## Verification and rectification feedback

After a deep reading, ask the user to mark major claims as `confirmed`, `partly confirmed`, `contradicted`, or `unknown`, and request a concrete example for high-impact contradictions. Use the result to update weighting and manifestation language.

When a birth time is revised or accepted from another rectification process:

- record the source and precision of the time;
- create a new canonical chart version;
- rerun the justified uncertainty interval;
- compare angles, house cusps, time-sensitive house placements, sect, angularity, and aspect stability;
- preserve the prior report and correction log;
- keep the other astrological system's doctrine out of Western evidence and synthesis.
