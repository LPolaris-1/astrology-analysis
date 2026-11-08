#!/usr/bin/env python3
"""Create a validated canonical Western tropical natal-chart artifact."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import birth_to_chart as engine


SCHEMA_VERSION = "western-natal-v1"
PIPELINE_VERSION = "1.0.0"
ALLOWED_HOUSE_SYSTEMS = {"Placidus", "Whole Sign"}
REQUIRED_BODIES = {
    "Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn",
    "Uranus", "Neptune", "Pluto", "True Node",
}
ASPECT_ANGLES = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}
FIXTURE_ASC = 174.5472
FIXTURE_MC = 83.6916
FIXTURE_TOLERANCE_DEG = 0.05


class PipelineError(ValueError):
    pass


def load_payload(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"Cannot read input JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PipelineError("Input JSON must be an object.")
    return data


def normalize_input(payload: dict[str, Any], ephe_path: Path) -> tuple[dict, dict]:
    location = payload.get("location")
    if not isinstance(location, dict):
        raise PipelineError("location must contain label, lat, lon, and timezone.")
    for key in ("lat", "lon", "timezone"):
        if location.get(key) in (None, ""):
            raise PipelineError(f"location.{key} is required; it is never guessed.")
    if not payload.get("date"):
        raise PipelineError("date is required.")

    precision = payload.get("time_precision") or {}
    if not isinstance(precision, dict):
        raise PipelineError("time_precision must be an object.")
    source = str(precision.get("source") or "unrecorded").strip()
    time_value = payload.get("time")
    unknown = time_value in (None, "")
    if unknown and source.lower() != "unknown":
        raise PipelineError(
            "Missing time requires time_precision.source='unknown'; refusing to "
            "silently substitute noon as a birth time."
        )
    uncertainty = precision.get("uncertainty_minutes", 0 if unknown else 1)
    try:
        uncertainty = int(uncertainty)
    except (TypeError, ValueError) as exc:
        raise PipelineError("time_precision.uncertainty_minutes must be an integer.") from exc
    if uncertainty < 0 or uncertainty > 60:
        raise PipelineError("uncertainty_minutes must be between 0 and 60.")

    house_system = str(payload.get("house_system") or "Placidus")
    if house_system not in ALLOWED_HOUSE_SYSTEMS:
        raise PipelineError(
            f"This skill validates only {sorted(ALLOWED_HOUSE_SYSTEMS)}, got {house_system!r}."
        )
    tradition_mode = str(payload.get("tradition_mode") or "blended")
    if tradition_mode not in {"classical", "modern", "blended"}:
        raise PipelineError("tradition_mode must be classical, modern, or blended.")

    cfg: dict[str, Any] = {
        "date": str(payload["date"]),
        "lat": float(location["lat"]),
        "lon": float(location["lon"]),
        "tz": str(location["timezone"]),
        "place": location.get("label"),
        "name": payload.get("subject"),
        "house_system": house_system,
        "ayanamsa": "tropical",
        "reading_type": "natal",
        "tradition_mode": tradition_mode,
        "tone": str(payload.get("tone") or "practical"),
        "ephe_path": str(ephe_path),
        "verbose": True,
    }
    if unknown:
        cfg["noon_for_unknown"] = True
        cfg["confidence"] = engine.CONF_UNKNOWN
    else:
        cfg["time"] = str(time_value)
        if str(source).lower() == "rectified":
            cfg["rectified"] = True
        elif uncertainty > 1 or str(source).lower() in {"family memory", "approximate"}:
            cfg["approximate"] = True
        else:
            cfg["confidence"] = engine.CONF_TIMED
    if payload.get("elevation_m") is not None:
        cfg["elevation"] = float(payload["elevation_m"])

    normalized = {
        "subject": payload.get("subject"),
        "date": cfg["date"],
        "time": None if unknown else cfg["time"],
        "location": {
            "label": location.get("label"),
            "lat": cfg["lat"],
            "lon": cfg["lon"],
            "timezone": cfg["tz"],
        },
        "house_system": house_system,
        "zodiac": "Tropical",
        "time_precision": {
            "uncertainty_minutes": uncertainty,
            "source": source,
        },
        "tradition_mode": tradition_mode,
        "tone": cfg["tone"],
    }
    return cfg, normalized


def angular_distance(a: float, b: float) -> float:
    delta = abs((a % 360.0) - (b % 360.0))
    return min(delta, 360.0 - delta)


def require_se1(chart: dict) -> None:
    mode = chart["chart_data"].get("calculation_meta", {}).get("ephemeris_mode")
    if mode != "Swiss Ephemeris .se1":
        raise PipelineError(
            f"Precision gate failed: expected 'Swiss Ephemeris .se1', got {mode!r}. "
            "Moshier or another silent fallback is not accepted."
        )


def validate_invariants(chart: dict, timed: bool) -> list[dict[str, Any]]:
    data = chart.get("chart_data")
    if not isinstance(data, dict):
        raise PipelineError("Calculator output lacks chart_data.")
    checks: list[dict[str, Any]] = []

    placements = data.get("placements")
    if not isinstance(placements, list):
        raise PipelineError("placements must be a list.")
    bodies = [p.get("body") for p in placements]
    missing = sorted(REQUIRED_BODIES - set(bodies))
    duplicates = sorted({b for b in bodies if bodies.count(b) > 1})
    if missing or duplicates:
        raise PipelineError(f"Body integrity failed; missing={missing}, duplicates={duplicates}")
    checks.append({"name": "required_bodies", "status": "passed", "count": len(bodies)})

    for placement in placements:
        lon = placement.get("absolute_degree")
        if not isinstance(lon, (int, float)) or not 0.0 <= float(lon) < 360.0:
            raise PipelineError(f"Invalid longitude for {placement.get('body')}: {lon!r}")
        house = placement.get("house")
        if timed and (not isinstance(house, int) or not 1 <= house <= 12):
            raise PipelineError(f"Invalid house for {placement.get('body')}: {house!r}")
    checks.append({"name": "placement_ranges", "status": "passed"})

    if timed:
        cusps = data.get("house_cusps")
        if not isinstance(cusps, list) or len(cusps) != 12:
            raise PipelineError("Timed chart must contain exactly 12 house cusps.")
        if not data.get("ascendant") or not data.get("midheaven"):
            raise PipelineError("Timed chart must contain Ascendant and Midheaven.")
        for expected, cusp in enumerate(cusps, start=1):
            if cusp.get("house") != expected:
                raise PipelineError("House cusps are not ordered 1 through 12.")
            lon = cusp.get("absolute_degree")
            if not isinstance(lon, (int, float)) or not 0.0 <= float(lon) < 360.0:
                raise PipelineError(f"Invalid cusp longitude for house {expected}: {lon!r}")
        checks.append({"name": "timed_factors", "status": "passed"})

    object_lons = {p["body"]: float(p["absolute_degree"]) for p in placements}
    if timed:
        object_lons["Ascendant"] = float(data["ascendant"]["absolute_degree"])
        object_lons["Midheaven"] = float(data["midheaven"]["absolute_degree"])
    seen: set[tuple[str, str, str]] = set()
    for aspect in data.get("aspects", []):
        a = aspect.get("body_a")
        b = aspect.get("body_b")
        kind = aspect.get("aspect")
        if a not in object_lons or b not in object_lons or kind not in ASPECT_ANGLES:
            raise PipelineError(f"Aspect references invalid objects or type: {aspect}")
        key = (*sorted((a, b)), kind)
        if key in seen:
            raise PipelineError(f"Duplicate aspect: {key}")
        seen.add(key)
        sep = angular_distance(object_lons[a], object_lons[b])
        expected_orb = abs(sep - ASPECT_ANGLES[kind])
        if abs(expected_orb - float(aspect.get("orb_degrees"))) > 0.0011:
            raise PipelineError(f"Aspect orb mismatch for {a} {kind} {b}.")
        if aspect.get("applying") and aspect.get("separating"):
            raise PipelineError(f"Aspect cannot be both applying and separating: {aspect}")
    checks.append({"name": "aspect_geometry", "status": "passed", "count": len(seen)})
    return checks


def precision_fixture(ephe_path: Path) -> dict[str, Any]:
    cfg = {
        "date": "1990-05-21",
        "time": "14:32",
        "lat": 40.7128,
        "lon": -74.0060,
        "tz": "America/New_York",
        "place": "New York",
        "house_system": "Placidus",
        "ayanamsa": "tropical",
        "reading_type": "natal",
        "tradition_mode": "blended",
        "tone": "technical",
        "ephe_path": str(ephe_path),
        "confidence": engine.CONF_TIMED,
    }
    chart = engine.build_chart(cfg)
    require_se1(chart)
    asc = float(chart["chart_data"]["ascendant"]["absolute_degree"])
    mc = float(chart["chart_data"]["midheaven"]["absolute_degree"])
    asc_error = angular_distance(asc, FIXTURE_ASC)
    mc_error = angular_distance(mc, FIXTURE_MC)
    if asc_error > FIXTURE_TOLERANCE_DEG or mc_error > FIXTURE_TOLERANCE_DEG:
        raise PipelineError(
            f"Precision fixture failed: Asc error={asc_error:.6f}°, MC error={mc_error:.6f}°."
        )
    return {
        "status": "passed",
        "fixture": "1990-05-21 14:32 America/New_York",
        "ascendant_error_degrees": round(asc_error, 6),
        "midheaven_error_degrees": round(mc_error, 6),
        "tolerance_degrees": FIXTURE_TOLERANCE_DEG,
        "ephemeris_mode": chart["chart_data"]["calculation_meta"]["ephemeris_mode"],
    }


def shifted_cfg(cfg: dict[str, Any], offset_minutes: int) -> dict[str, Any]:
    shifted = copy.deepcopy(cfg)
    time_text = str(cfg["time"])
    time_format = "%H:%M:%S" if time_text.count(":") == 2 else "%H:%M"
    base = datetime.strptime(f"{cfg['date']} {time_text}", f"%Y-%m-%d {time_format}")
    value = base + timedelta(minutes=offset_minutes)
    shifted["date"] = value.strftime("%Y-%m-%d")
    shifted["time"] = value.strftime(time_format)
    return shifted


def aspect_signature(aspect: dict[str, Any]) -> str:
    a, b = sorted((str(aspect["body_a"]), str(aspect["body_b"])))
    return f"{a}|{aspect['aspect']}|{b}"


def longitude_span(values: list[float]) -> float:
    if not values:
        return 0.0
    unwrapped = [values[0]]
    for value in values[1:]:
        candidate = value
        while candidate - unwrapped[-1] > 180.0:
            candidate -= 360.0
        while candidate - unwrapped[-1] < -180.0:
            candidate += 360.0
        unwrapped.append(candidate)
    return max(unwrapped) - min(unwrapped)


def audit_stability(cfg: dict[str, Any], uncertainty: int) -> dict[str, Any]:
    if cfg.get("time") is None:
        return {"status": "not_applicable", "reason": "birth time unknown"}
    offsets = list(range(-uncertainty, uncertainty + 1))
    samples = [engine.build_chart(shifted_cfg(cfg, offset)) for offset in offsets]
    for sample in samples:
        require_se1(sample)
    data = [sample["chart_data"] for sample in samples]

    asc_signs = sorted({item["ascendant"]["sign"] for item in data})
    mc_signs = sorted({item["midheaven"]["sign"] for item in data})
    asc_lons = [float(item["ascendant"]["absolute_degree"]) for item in data]
    mc_lons = [float(item["midheaven"]["absolute_degree"]) for item in data]

    cusp_changes: list[int] = []
    for house in range(1, 13):
        signs = {item["house_cusps"][house - 1]["sign"] for item in data}
        if len(signs) > 1:
            cusp_changes.append(house)

    house_sets: dict[str, set[int]] = {body: set() for body in REQUIRED_BODIES}
    for item in data:
        for placement in item["placements"]:
            if placement["body"] in house_sets:
                house_sets[placement["body"]].add(int(placement["house"]))
    sensitive_houses = {
        body: sorted(values) for body, values in sorted(house_sets.items()) if len(values) > 1
    }

    aspect_sets = [set(aspect_signature(a) for a in item.get("aspects", [])) for item in data]
    stable_aspects = set.intersection(*aspect_sets) if aspect_sets else set()
    all_aspects = set.union(*aspect_sets) if aspect_sets else set()
    sensitive_aspects = sorted(all_aspects - stable_aspects)

    sect_statuses = sorted({str(item.get("sect", {}).get("status")) for item in data})
    lot_signs: set[str] = set()
    lot_houses: set[int] = set()
    lot_formulas: set[str] = set()
    for item in data:
        lots = item.get("lots") or []
        if lots:
            lot = lots[0]
            lot_signs.add(str(lot.get("sign")))
            lot_houses.add(int(lot.get("house")))
            lot_formulas.add(str(lot.get("formula")))
    lot_sensitive = len(lot_signs) > 1 or len(lot_houses) > 1 or len(lot_formulas) > 1

    overall_sensitive = bool(
        len(asc_signs) > 1 or len(mc_signs) > 1 or cusp_changes
        or sensitive_houses or sensitive_aspects or len(sect_statuses) > 1
        or lot_sensitive
    )
    return {
        "status": "boundary_sensitive" if overall_sensitive else "stable",
        "window_minutes": uncertainty,
        "sample_count": len(samples),
        "offsets_minutes": offsets,
        "ascendant": {
            "status": "stable" if len(asc_signs) == 1 else "boundary_sensitive",
            "signs": asc_signs,
            "longitude_span_degrees": round(longitude_span(asc_lons), 6),
        },
        "midheaven": {
            "status": "stable" if len(mc_signs) == 1 else "boundary_sensitive",
            "signs": mc_signs,
            "longitude_span_degrees": round(longitude_span(mc_lons), 6),
        },
        "house_cusp_signs": {
            "status": "stable" if not cusp_changes else "boundary_sensitive",
            "changed_houses": cusp_changes,
        },
        "planet_houses": {
            "status": "stable" if not sensitive_houses else "boundary_sensitive",
            "boundary_sensitive": sensitive_houses,
        },
        "aspects": {
            "status": "stable" if not sensitive_aspects else "boundary_sensitive",
            "stable_count": len(stable_aspects),
            "boundary_sensitive": sensitive_aspects,
        },
        "sect": {
            "status": "stable" if len(sect_statuses) == 1 else "boundary_sensitive",
            "possible_values": sect_statuses,
        },
        "lot_of_fortune": {
            "status": "stable" if not lot_sensitive else "boundary_sensitive",
            "signs": sorted(lot_signs),
            "houses": sorted(lot_houses),
            "formulas": sorted(lot_formulas),
        },
    }


def build_canonical(payload: dict[str, Any], skill_dir: Path) -> dict[str, Any]:
    ephe_path = skill_dir / "scripts" / "ephe"
    if not ephe_path.is_dir():
        raise PipelineError(f"Ephemeris directory missing: {ephe_path}")
    fixture = precision_fixture(ephe_path)
    cfg, normalized = normalize_input(payload, ephe_path)
    chart = engine.build_chart(cfg)
    require_se1(chart)
    timed = cfg.get("time") is not None
    invariant_checks = validate_invariants(chart, timed=timed)
    uncertainty = int(normalized["time_precision"]["uncertainty_minutes"])
    stability = audit_stability(cfg, uncertainty)
    input_level = (
        "not_available" if stability["status"] == "not_applicable"
        else "moderate" if stability["status"] == "boundary_sensitive"
        else "high"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generator": {
            "name": "astrology-analysis natal_pipeline.py",
            "version": PIPELINE_VERSION,
        },
        "input_normalized": normalized,
        "calculation": chart,
        "validation": {
            "status": "passed",
            "precision_fixture": fixture,
            "invariants": invariant_checks,
        },
        "input_stability": stability,
        "confidence": {
            "calculation": "high",
            "input_stability": input_level,
            "structural_convergence": "not_evaluated",
            "interpretation": "not_evaluated",
            "external_validation": "not_validated",
        },
        "correction_log": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate validated canonical Western natal chart data."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input JSON path")
    parser.add_argument("--output", required=True, type=Path, help="Output chart_data.json path")
    args = parser.parse_args()
    try:
        payload = load_payload(args.input)
        canonical = build_canonical(payload, Path(__file__).resolve().parent.parent)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(canonical, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except (PipelineError, engine.ConfigError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"PASS: {args.output}")
    print("backend=Swiss Ephemeris .se1")
    print(f"stability={canonical['input_stability']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
