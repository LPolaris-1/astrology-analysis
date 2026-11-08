# NOTICE — Swiss Ephemeris calculation tooling

The files under `scripts/` provide deterministic natal-chart calculation,
validation, time-stability auditing, and self-tests for the `astrology-analysis`
Skill. They use `pyswisseph`, the Python binding for Swiss Ephemeris.

## Licensing — read before use

`birth_to_chart.py` depends on **pyswisseph**, the Python binding for the
**Swiss Ephemeris**. Swiss Ephemeris and pyswisseph are **dual-licensed**:

1. **GNU AGPL-3.0** (the default, free option), **or**
2. the **Swiss Ephemeris Professional License** from Astrodienst
   (https://www.astro.com/swisseph/) — the paid, commercial option.

Accordingly, the Swiss Ephemeris calculation tooling in `scripts/` is
distributed under GNU AGPL-3.0 unless the user has obtained and applies the
Swiss Ephemeris Professional License. The complete AGPL text is included as
`licenses/swiss-ephemeris-tooling-AGPL-3.0.txt`.

Interpretive references and report-writing instructions are maintained under
their separately stated terms. See `licenses/interpretive-resources-MIT.txt`
and `references/source_canon_and_rights_ledger.md`.

### If you cannot accept AGPL

You **must** purchase the Swiss Ephemeris Professional License from
Astrodienst and use pyswisseph under those terms. This choice is yours to
make and to record; this repo does not grant you that license.

## Third-party attribution

- **Swiss Ephemeris** — © Astrodienst AG, Zurich, Switzerland.
  https://www.astro.com/swisseph/
  Planetary positions are derived from the Swiss Ephemeris / JPL DE431.
  Ephemeris data files (`.se1`), if you choose to download them, are freely
  redistributable from Astrodienst's download area provided this copyright
  notice is preserved.

## Ephemeris data files are not bundled

This repository ships **no** `.se1` ephemeris data files. The Skill's
precision gate intentionally refuses Moshier fallback. Download the required
`.se1` files from Astrodienst's official distribution channel and place them
under `scripts/ephe/` before running `scripts/self_test.py` or the natal
pipeline. Do not commit `.se1` files into this repository.
