"""Score separately adjudicated phonetic contrasts. This is an offline audit tool."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re


SHA256 = re.compile(r"[0-9a-f]{64}")
REFERENCE_VALUES = {"target_error", "valid", "other_error", "ambiguous"}
PREDICTION_VALUES = {"target_alert", "clear", "other_alert", "abstain"}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Repeated JSON key")
        result[key] = value
    return result


def read_json(path, digest=None):
    data = path.read_bytes()
    if digest is not None and sha256(data).hexdigest() != digest.casefold():
        raise ValueError("The sealed file does not match its SHA-256")
    return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique_object)


def index_cases(cases):
    indexed = {}
    recordings = {}
    cohorts = {}
    for case in cases:
        key = case["id"]
        speaker = case["speaker"].strip().casefold()
        prompt, audio = (case[name] for name in ("prompt_sha256", "audio_sha256"))
        expected, intended = (case[name].strip() for name in ("expected", "target"))
        if not key or key in indexed or not speaker or not expected or not intended or expected == intended:
            raise ValueError("Invalid or repeated case, missing speaker, or invalid contrast")
        if not SHA256.fullmatch(prompt) or not SHA256.fullmatch(audio):
            raise ValueError("Cases require normalized prompt and recording SHA-256 fingerprints")
        cohort = case["cohort"]
        if cohort not in {"learner", "british_control"}:
            raise ValueError("Unknown cohort")
        if cohorts.setdefault(speaker, cohort) != cohort:
            raise ValueError("The same speaker appears in incompatible cohorts")
        if recordings.setdefault(audio, (speaker, prompt)) != (speaker, prompt):
            raise ValueError("The same recording is attributed to different speakers or prompts")
        indexed[key] = {**case, "speaker": speaker, "expected": expected, "target": intended}
    return indexed


def compare_partitions(development, final):
    for field in ("speaker", "prompt_sha256", "audio_sha256"):
        a = {case[field] for case in development.values()}
        b = {case[field] for case in final.values()}
        if a & b:
            raise ValueError(f"Development and final partitions overlap by {field}")


def verdict(first, second, arbiter=None):
    notes = [first, second] if arbiter is None else [first, second, arbiter]
    identities = {note["reviewer"].strip().casefold() for note in notes}
    if "" in identities or len(identities) != len(notes):
        raise ValueError("Reviewers and the adjudicator require distinct reviewer IDs")
    if any(note["verdict"] not in REFERENCE_VALUES for note in notes):
        raise ValueError("Unknown review verdict")
    if first["verdict"] == second["verdict"]:
        if arbiter is not None:
            raise ValueError("Adjudication is only used when independent reviews differ")
        return first["verdict"]
    return arbiter["verdict"] if arbiter is not None else "ambiguous"


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def score(development, final, first, second, arbiters, predictions):
    development = index_cases(development)
    final = index_cases(final)
    if not development or not final:
        raise ValueError("Supply non-empty development and final manifests")
    compare_partitions(development, final)
    for supplied in (first, second, predictions):
        if supplied.keys() != final.keys():
            raise ValueError("Both reviews and predictions must cover the sealed manifest exactly")
    if not arbiters.keys() <= final.keys():
        raise ValueError("An adjudication refers to a case outside the sealed manifest")

    rows = defaultdict(Counter)
    speakers = defaultdict(set)
    for key, case in final.items():
        contrast = (case["expected"], case["target"])
        reference = verdict(first[key], second[key], arbiters.get(key))
        prediction = predictions[key]
        if prediction not in PREDICTION_VALUES:
            raise ValueError("Unknown prediction")
        count = rows[contrast]
        count["cases"] += 1
        count["positives"] += reference == "target_error"
        count["legitimate_controls"] += reference == "valid"
        count["british_controls"] += reference == "valid" and case["cohort"] == "british_control"
        count["other_reference_errors"] += reference == "other_error"
        count["unresolved"] += reference == "ambiguous"
        count["model_abstentions"] += prediction == "abstain"
        count["auditable_decisions"] += reference != "ambiguous" and prediction != "abstain"
        count["alerts"] += prediction in {"target_alert", "other_alert"}
        count["true_positives"] += reference == "target_error" and prediction == "target_alert"
        count["alerts_on_legitimate_controls"] += reference == "valid" and prediction in {"target_alert", "other_alert"}
        if reference in {"target_error", "valid"}:
            speakers[contrast].add(case["speaker"])

    report = []
    for contrast, counts in sorted(rows.items()):
        n, p, a, covered, tp = (counts[k] for k in ("cases", "positives", "alerts", "auditable_decisions", "true_positives"))
        gates = {
            "sensitivity_at_least_80": p > 0 and tp * 100 >= p * 80,
            "precision_at_least_95": a > 0 and tp * 100 >= a * 95,
            "coverage_at_least_90": covered * 100 >= n * 90,
            "sample_minimum": p >= 20 and counts["legitimate_controls"] >= 20 and len(speakers[contrast]) >= 4,
            "british_controls_present": counts["british_controls"] > 0,
        }
        report.append({"expected": contrast[0], "target": contrast[1], **counts,
                       "voices_with_confirmed_targets": len(speakers[contrast]),
                       "missed_effective": p - tp, "incorrect_or_unconfirmed_alerts": a - tp,
                       "effective_sensitivity": ratio(tp, p), "precision": ratio(tp, a),
                       "auditable_coverage": ratio(covered, n),
                       "model_coverage": ratio(n - counts["model_abstentions"], n),
                       "gates": gates, "passes_technical_metrics": all(gates.values())})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--development", type=Path, required=True)
    parser.add_argument("--final", type=Path, required=True)
    parser.add_argument("--final-sha256", required=True)
    parser.add_argument("--review-a", type=Path, required=True)
    parser.add_argument("--review-b", type=Path, required=True)
    parser.add_argument("--adjudications", type=Path)
    parser.add_argument("--predictions", type=Path, required=True)
    args = parser.parse_args()
    try:
        results = score(read_json(args.development), read_json(args.final, args.final_sha256),
                        read_json(args.review_a), read_json(args.review_b),
                        read_json(args.adjudications) if args.adjudications else {}, read_json(args.predictions))
    except (KeyError, TypeError, ValueError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(results, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
