# Calculation and validation contract

## Input JSON

```json
{
  "subject": "optional label",
  "date": "2000-01-01",
  "time": "12:34",
  "location": {
    "label": "City, Country",
    "lat": 0.0,
    "lon": 0.0,
    "timezone": "Area/City"
  },
  "house_system": "Placidus",
  "time_precision": {
    "uncertainty_minutes": 5,
    "source": "birth certificate | family memory | approximate | unknown"
  },
  "tradition_mode": "blended",
  "tone": "practical"
}
```

For an unknown time, omit `time` and set `time_precision.source` to `unknown`. The pipeline creates an explicit noon-reference chart and omits time-dependent factors. It never treats noon as the birth time.

Supported house systems for this skill are `Placidus` and `Whole Sign`. The underlying calculator contains other systems, but they are outside the tested natal contract.

## Canonical artifact

`chart_data.json` contains:

- `schema_version` and generator provenance;
- normalized input and calculation options;
- the deterministic chart from Swiss Ephemeris;
- automatic invariant checks;
- birth-time perturbation audit;
- five confidence dimensions;
- an initially empty correction log.

The report reads this artifact and never recomputes it.

## Hard validation gates

The pipeline must fail when:

- timezone, coordinates, or required birth fields are missing or invalid;
- the actual ephemeris mode is not `Swiss Ephemeris .se1`;
- a longitude is outside `[0, 360)`;
- required bodies are missing or duplicated;
- a timed chart lacks 12 houses, Ascendant, or Midheaven;
- a house assignment is outside `1..12`;
- an aspect's orb, exact angle, or applying/separating flags are inconsistent;
- the fixed precision fixture exceeds tolerance.

Do not downgrade these failures to warnings.

## Time uncertainty

Choose `uncertainty_minutes` from evidence:

- exact minute from a record: normally `1` unless the record's semantics are uncertain;
- explicit family recollection: often `5` to `15`;
- rounded quarter-hour or wider: use the stated interval;
- unknown: no timed factors.

The audit resamples every minute in the interval (capped by the script) and reports stability separately for Ascendant, MC, cusp signs, planet houses, and aspect presence. A stable sign does not imply a stable degree; retain the recorded longitude span.

## Ephemeris and license boundary

The local `.se1` files and calculation script are governed by the Swiss Ephemeris/AGPL notice in `licenses/`. Interpretive references keep their own MIT/public-domain source ledger. Do not publish or redistribute the bundle without rechecking those terms.
