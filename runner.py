"""
EITE Benchmark v3 — Test execution runner.
Loads adapter, runs tests, calculates scores, generates diagnosis, saves results.
"""
import importlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import threading
from adapter import EiteAdapter
from base_test import BaseTest
from fix_registry import get_diagnosis


def _run_with_timeout(test: BaseTest) -> "TestResult":
    """Run a single test with a timeout to prevent hanging."""
    result = None
    exc = None

    def _target():
        nonlocal result, exc
        try:
            result = test.run()
        except Exception as e:
            exc = e

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout=test.timeout)

    if t.is_alive():
        # Test timed out
        test.result.status = "FAIL"
        test.result.trace = f"Timeout after {test.timeout}s"
        test.result.expected = "Complete within timeout"
        test.result.actual = f"Hung for >{test.timeout}s"
        test.cleanup()
        return test.result

    if exc:
        test.result.status = "FAIL"
        test.result.trace = f"Thread exception: {exc}"
        test.cleanup()
        return test.result

    return result or test.result

RESULTS_DIR = Path(__file__).parent / "results"
STAGES = [
    "tool_precision",
    "startup", "comms", "detection", "execution",
    "response", "error_handling", "identity",
    "semantic_repair", "cognitive_layer", "eite_identity", "essence_engine",
    "stability",
]


def load_adapter(name: str = None) -> EiteAdapter:
    """Load an adapter by name."""
    name = name or os.environ.get("EITE_ADAPTER", "stub")
    # Try adapters/ package
    try:
        mod = importlib.import_module(f"adapters.{name}")
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (isinstance(attr, type)
                    and issubclass(attr, EiteAdapter)
                    and attr is not EiteAdapter):
                return attr()
    except ImportError:
        pass
    # Try as dotted path
    try:
        mod = importlib.import_module(name)
        for attr_name in dir(mod):
            attr = getattr(mod, attr_name)
            if (isinstance(attr, type)
                    and issubclass(attr, EiteAdapter)
                    and attr is not EiteAdapter):
                return attr()
    except ImportError:
        pass
    raise ValueError(f"Cannot load adapter: {name!r}")


def load_tests(stage: str | None = None) -> list[BaseTest]:
    """Load all BaseTest subclasses from the tests/ package."""
    all_tests = []
    targets = [stage] if stage else STAGES
    for target in targets:
        try:
            module = importlib.import_module(f"tests.{target}")
        except ImportError:
            continue
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type)
                    and issubclass(attr, BaseTest)
                    and attr is not BaseTest
                    and getattr(attr, "test_id", "UNKNOWN") != "UNKNOWN"):
                all_tests.append(attr())
    all_tests.sort(key=lambda t: t.test_id)
    return all_tests


def load_previous_history() -> dict[str, list[str]]:
    """Load history from the most recent result file."""
    files = sorted(RESULTS_DIR.glob("*.json"))
    if not files:
        return {}
    with open(files[-1], "r", encoding="utf-8") as f:
        data = json.load(f)
    return {t["id"]: t.get("history", []) for t in data.get("tests", [])}


def run_suite(adapter: EiteAdapter | str | None = None, target_stage: str | None = None) -> dict:
    """Execute tests and return the full result payload with diagnosis.
    
    Backward compatible: run_suite("identity") works (string arg1 = stage name).
    Preferred: run_suite(adapter, "identity") or run_suite(adapter=MyAdapter(), target_stage="identity").
    """
    # Backward compat: if adapter is a string, treat it as target_stage
    if isinstance(adapter, str):
        target_stage = adapter
        adapter = None
    
    if adapter is None:
        adapter = load_adapter()
    
    tests = load_tests(target_stage)
    history_map = load_previous_history()

    for test in tests:
        test.adapter = adapter

    all_results = []
    stage_stats = {s: {"pass": 0, "fail": 0, "score": 0} for s in STAGES}

    for test in tests:
        result = _run_with_timeout(test)
        rdict = result.to_dict()
        prev = history_map.get(result.id, [])
        rdict["history"] = (prev[-9:] + [result.status])
        all_results.append(rdict)

        stage_key = result.stage
        if stage_key not in stage_stats:
            stage_stats[stage_key] = {"pass": 0, "fail": 0, "score": 0}
        if result.status == "PASS":
            stage_stats[stage_key]["pass"] += 1
        elif result.status == "FAIL":
            stage_stats[stage_key]["fail"] += 1

    total_pass = sum(1 for r in all_results if r["status"] == "PASS")
    total_fail = sum(1 for r in all_results if r["status"] == "FAIL")
    total_skip = sum(1 for r in all_results if r["status"] == "SKIP")
    total_count = total_pass + total_fail
    total_score = int((total_pass / total_count) * 100) if total_count else 0

    for stats in stage_stats.values():
        st = stats["pass"] + stats["fail"]
        stats["score"] = int((stats["pass"] / st) * 100) if st else 0

    # Generate diagnosis
    diagnosis = get_diagnosis(all_results)

    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%d-%H%M%S")
    payload = {
        "run_id": run_id,
        "timestamp": now.isoformat(),
        "adapter": {"name": adapter.name, "version": adapter.version},
        "total": {
            "pass": total_pass,
            "fail": total_fail,
            "skip": total_skip,
            "score": total_score,
        },
        "stages": stage_stats,
        "tests": all_results,
        "diagnosis": diagnosis,
    }

    # Atomic write
    RESULTS_DIR.mkdir(exist_ok=True)
    target = RESULTS_DIR / f"{run_id}.json"
    fd, tmp_path = tempfile.mkstemp(dir=RESULTS_DIR, suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        Path(tmp_path).replace(target)
    except Exception:
        os.unlink(tmp_path)
        raise

    return payload


def get_latest_results() -> dict | None:
    files = sorted(RESULTS_DIR.glob("*.json"))
    if not files:
        return None
    with open(files[-1], "r", encoding="utf-8") as f:
        return json.load(f)


def get_history() -> list[dict]:
    history = []
    for file in sorted(RESULTS_DIR.glob("*.json")):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        history.append({
            "run_id": data["run_id"],
            "timestamp": data["timestamp"],
            "adapter": data.get("adapter", {}),
            "score": data["total"]["score"],
        })
    return history
