# AGENTS.md

## Purpose

This repository is the portable publication source for the `astrology-analysis` Codex skill. It contains deterministic Western tropical natal-chart calculation, evidence-led interpretation instructions, and the references required by the skill.

## Boundaries

- Do not commit personal birth data, generated charts, private reports, correction logs, credentials, local registry files, staging reviews, archives, or absolute user paths.
- Do not commit `__pycache__`, virtual environments, generated output, or `.se1` ephemeris files.
- Keep Western tropical rules separate from Vedic, Chinese, horary, electional, and mundane astrology.
- Treat `chart_data.json` as the calculation source of truth; interpretation code and prompts must not recalculate placements.
- Preserve the Swiss Ephemeris licensing boundary and all files under `licenses/`.

## Structure

- `SKILL.md`: discovery, scope, core workflow, and output contract.
- `agents/openai.yaml`: UI metadata and invocation policy.
- `scripts/`: deterministic calculation and self-test tools.
- `references/`: calculation contract, analysis workflow, doctrine, and report guidance.
- `licenses/`: third-party notices and license texts.

## Verification

Before committing a functional change:

1. `python -X utf8 scripts/self_test.py`
2. `python -X utf8 scripts/natal_pipeline.py --input <input.json> --output <chart_data.json>`
3. Run the Codex `skill-creator` quick validator against the repository root when available.
4. Confirm no personal data, generated charts, cache files, or `.se1` data are staged.

Documentation-only changes must still preserve links, trigger boundaries, and the output contract.

## Release discipline

- Use narrow commits with explicit paths.
- Run `git diff --check` before publishing.
- Never force-push or rewrite published history.
- Keep the active installed Skill and this repository synchronized through a reviewed, verified update; do not edit two divergent copies independently.
