#!/usr/bin/env python3
"""Offline precision and behavior gate for astrology-analysis."""

from __future__ import annotations

import json
from pathlib import Path

import birth_to_chart as engine
import natal_pipeline as pipeline


def assert_raises(fn, message_fragment: str) -> None:
    try:
        fn()
    except Exception as exc:
        if message_fragment not in str(exc):
            raise AssertionError(f"Unexpected error: {exc}") from exc
    else:
        raise AssertionError("Expected an exception, but the call succeeded.")


def main() -> int:
    skill_dir = Path(__file__).resolve().parent.parent
    ephe_path = skill_dir / "scripts" / "ephe"

    fixture = pipeline.precision_fixture(ephe_path)
    assert fixture["ephemeris_mode"] == "Swiss Ephemeris .se1"

    def missing_timezone() -> None:
        engine.resolve_timezone(None, False, 0.0)

    assert_raises(missing_timezone, "No timezone supplied")

    tz, _label, _kind = engine.resolve_timezone("America/New_York", False, -74.006)
    utc = engine.wallclock_to_ut(1990, 5, 21, 14, 32, 0, tz)
    assert utc.isoformat().startswith("1990-05-21T18:32:00"), utc.isoformat()

    base = {
        "subject": "self-test",
        "date": "1990-05-21",
        "time": "14:32",
        "location": {
            "label": "New York",
            "lat": 40.7128,
            "lon": -74.0060,
            "timezone": "America/New_York",
        },
        "house_system": "Placidus",
        "time_precision": {"uncertainty_minutes": 5, "source": "test fixture"},
        "tradition_mode": "blended",
        "tone": "technical",
    }
    canonical = pipeline.build_canonical(base, skill_dir)
    assert canonical["validation"]["status"] == "passed"
    assert canonical["input_stability"]["sample_count"] == 11
    assert canonical["confidence"]["calculation"] == "high"
    assert canonical["input_stability"]["sect"]["status"] in {"stable", "boundary_sensitive"}
    assert canonical["input_stability"]["lot_of_fortune"]["status"] in {"stable", "boundary_sensitive"}

    with_seconds = dict(base)
    with_seconds["time"] = "14:32:20"
    second_chart = pipeline.build_canonical(with_seconds, skill_dir)
    source = second_chart["calculation"]["chart_data"]["source_notes"]
    assert "time 14:32:20" in source

    whole_sign = dict(base)
    whole_sign["house_system"] = "Whole Sign"
    whole = pipeline.build_canonical(whole_sign, skill_dir)
    assert whole["calculation"]["chart_data"]["house_system"] == "Whole Sign"

    unknown = {
        "date": "1990-05-21",
        "location": base["location"],
        "time_precision": {"source": "unknown", "uncertainty_minutes": 0},
    }
    unknown_chart = pipeline.build_canonical(unknown, skill_dir)
    unknown_data = unknown_chart["calculation"]["chart_data"]
    assert "ascendant" not in unknown_data
    assert unknown_chart["input_stability"]["status"] == "not_applicable"

    # Regression for the upstream topocentric-Moon bug: observer coordinates
    # must affect the result instead of being replaced by (0, 0).
    jd = engine.ut_to_jd(utc)
    bodies = [("Moon", engine.swe.MOON, engine.SPEED_LUMINARY)]
    flags = engine._flags(False, topo=False)
    engine.swe.set_ephe_path(str(ephe_path))
    p1, mode1 = engine.compute_positions(
        jd, bodies, flags, True, 100.0, observer_lon=-74.006, observer_lat=40.7128
    )
    p2, mode2 = engine.compute_positions(
        jd, bodies, flags, True, 100.0, observer_lon=139.6917, observer_lat=35.6895
    )
    assert mode1 == mode2 == "Swiss Ephemeris .se1"
    assert p1[0]["absolute_degree"] != p2[0]["absolute_degree"]

    serialized = json.dumps(canonical, ensure_ascii=False)
    reread = json.loads(serialized)
    assert reread["schema_version"] == pipeline.SCHEMA_VERSION

    print("PASS: astrology-analysis self-test")
    print("backend=Swiss Ephemeris .se1")
    print(
        "fixture_errors="
        f"Asc {fixture['ascendant_error_degrees']}°, "
        f"MC {fixture['midheaven_error_degrees']}°"
    )
    print("validated=timezone,DST,Placidus,Whole Sign,unknown-time,stability,topocentric")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
