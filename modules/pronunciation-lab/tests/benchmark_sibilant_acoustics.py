"""Offline /z/ to /s/ feasibility with frozen IF-MDD predictions and Praat."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from statistics import median
import sys
from tempfile import gettempdir
from time import perf_counter

import numpy as np
import parselmouth

from benchmark_l2_arctic import SAMPLE_COUNT, SPEAKERS, tiers

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lab import load_audio


ARPA = frozenset((
    "AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH IY JH K L M N NG "
    "OW OY P R S SH T TH UH UW V W Y Z ZH"
).split())
CALIBRATION = ("EBVS", "ERMS", "MBMPS")
EVALUATION = ("NJS",)
VOICING_CUTS = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
CACHE = Path(gettempdir())
SIBILANTS = {"S", "Z"}


def phone(value):
    return re.sub(r"[012]$", "", value.strip().upper())


def annotate(grid):
    words = [(start, end) for start, end, word in grid["words"] if re.fullmatch(r"[a-zA-Z']+", word)]
    canonical = []
    targets = []
    for start, end, raw in grid["phones"]:
        label = tuple(phone(part) for part in raw.split(","))
        expected = label[0]
        if expected not in ARPA:
            continue
        if label in (("Z",), ("Z", "S", "S")):
            midpoint = (start + end) / 2
            if any(lo <= midpoint < hi for lo, hi in words):
                targets.append((len(canonical), label == ("Z", "S", "S"), start, end))
        canonical.append(expected)
    return canonical, targets


def align_indices(canonical, observed):
    """Trace the historical unit-cost alignment with diagonal-first ties."""
    costs = [list(range(len(observed) + 1))]
    for i, expected in enumerate(canonical, 1):
        costs.append([i])
        for j, emitted in enumerate(observed, 1):
            costs[i].append(min(
                costs[i-1][j-1] + (expected != emitted), costs[i-1][j] + 1, costs[i][j-1] + 1,
            ))
    assigned = [None] * len(canonical)
    i, j = len(canonical), len(observed)
    while i or j:
        if i and j and costs[i][j] == costs[i-1][j-1] + (canonical[i-1] != observed[j-1]):
            assigned[i-1] = j-1
            i, j = i-1, j-1
        elif i and costs[i][j] == costs[i-1][j] + 1:
            i -= 1
        else:
            j -= 1
    return assigned


def inferred_window(centers, index, duration):
    center = centers[index]
    start = max(0, center - 0.070)
    end = min(duration, center + 0.070)
    if index > 0:
        start = max(start, (centers[index-1] + center) / 2)
    if index + 1 < len(centers):
        end = min(end, (center + centers[index+1]) / 2)
    return start, end


def acoustic_frames(samples, rate):
    """Combine frication-band power with periodicity at common Praat frames."""
    pitch = parselmouth.Sound(samples, sampling_frequency=rate).to_pitch_ac(
        time_step=0.005, pitch_floor=75, pitch_ceiling=400,
    )
    times = pitch.xs()
    periodic = pitch.selected_array["frequency"] > 0
    frication = np.zeros(times.size, dtype=bool)
    width = round(0.016 * rate)
    taper = np.hanning(width)
    bands = np.fft.rfftfreq(width, d=1/rate)
    high_band = (bands >= 2500) & (bands <= 7500)
    audible_band = (bands >= 80) & (bands <= 7500)
    floor = max(1e-4, np.sqrt(np.mean(samples**2)) * 0.08)
    for index, time in enumerate(times):
        start = round(time * rate) - width // 2
        frame = samples[start:start + width]
        if frame.size != width or np.sqrt(np.mean(frame**2)) < floor:
            continue
        spectrum = np.abs(np.fft.rfft(frame * taper)) ** 2
        total_power = np.sum(spectrum[audible_band])
        frication[index] = total_power > 0 and np.sum(spectrum[high_band]) / total_power >= 0.18
    return times, periodic, frication


def voicing(frames, start, end):
    if end - start < 0.025:
        return None
    times, periodic, frication = frames
    trim = (end - start) * 0.15
    active = (times >= start + trim) & (times <= end - trim) & frication
    if np.count_nonzero(active) < 3:
        return None
    return float(np.mean(periodic[active]))


def collect(cache, observations):
    results = []
    audio_seconds = 0.0
    for speaker in SPEAKERS:
        folder = cache / speaker
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        if len(manifest) != SAMPLE_COUNT:
            raise ValueError(f"Unexpected manifest size for {speaker}")
        for item in manifest:
            stem = item["id"]
            identity = f"{speaker}/{stem}"
            annotation = folder / f"{stem}.TextGrid"
            source = folder / f"{stem}.wav"
            for key, path in (("TextGrid", annotation), ("wav", source)):
                if sha256(path.read_bytes()).hexdigest() != item["sha256"][key]:
                    raise ValueError(f"Cache hash changed for {identity}")
            canonical, targets = annotate(tiers(annotation.read_text(encoding="utf-8-sig")))
            if not targets:
                continue
            emitted = [row for row in observations[identity]["phones"] if phone(row["phone"]) in ARPA]
            decoded = [phone(row["phone"]) for row in emitted]
            centers = [float(row["center_seconds"]) for row in emitted]
            if centers != sorted(centers):
                raise ValueError(f"Nonmonotonic emission times for {identity}")
            alignment = align_indices(canonical, decoded)
            samples, rate = load_audio(source)
            duration = len(samples) / rate
            audio_seconds += duration
            frames = acoustic_frames(samples, rate)
            for slot, positive, gold_start, gold_end in targets:
                index = alignment[slot]
                overlap = None
                inferred = None
                predicted = None
                if index is not None:
                    predicted = decoded[index]
                    start, end = inferred_window(centers, index, duration)
                    intersection = max(0, min(end, gold_end) - max(start, gold_start))
                    union = max(end, gold_end) - min(start, gold_start)
                    overlap = intersection / union
                    inferred = voicing(frames, start, end)
                results.append({
                    "speaker": speaker, "positive": positive, "emitted": predicted,
                    "oracle_voicing": voicing(frames, gold_start, gold_end), "inferred_voicing": inferred,
                    "overlap": overlap,
                })
    return results, audio_seconds


def summarize(rows, decision):
    counts = Counter()
    for row in rows:
        positive = row["positive"]
        flag = decision(row)
        if flag is None:
            counts["positive_abstentions" if positive else "control_abstentions"] += 1
        elif flag:
            counts["tp" if positive else "fp"] += 1
        else:
            counts["fn" if positive else "tn"] += 1
    tp, fp, fn, tn = (counts[k] for k in ("tp", "fp", "fn", "tn"))
    positive, control = counts["positive_abstentions"], counts["control_abstentions"]
    def ratio(n, d):
        return n / d if d else None
    return {
        "tp": tp, "fp": fp, "fn_evaluated": fn, "fn_effective": fn + positive, "tn": tn,
        "positive_abstentions": positive, "control_abstentions": control,
        "precision": ratio(tp, tp + fp), "effective_sensitivity": ratio(tp, tp + fn + positive),
        "specificity": ratio(tn, tn + fp), "effective_specificity": ratio(tn, tn + fp + control),
        "effective_f1": ratio(2*tp, 2*tp + fp + fn + positive),
        "coverage": ratio(tp + fp + fn + tn, len(rows)),
    }


def acoustic_decision(row, feature, threshold, require_agreement=False):
    measured = row[feature]
    emitted = row["emitted"]
    if measured is None:
        return None
    candidate = measured <= threshold
    if require_agreement and (emitted not in SIBILANTS or candidate != (emitted == "S")):
        return None
    return candidate


def fit(calibration, evaluation, feature, require_agreement):
    rows = []
    for threshold in VOICING_CUTS:
        decision = lambda row: acoustic_decision(row, feature, threshold, require_agreement)
        rows.append({"threshold": threshold, **summarize(calibration, decision)})
    passing = [r for r in rows if (r["precision"] or 0) >= 0.90 and r["effective_sensitivity"] >= 0.60
               and r["coverage"] >= 0.75 and r["tp"] + r["fp"] >= 10]
    chosen = max(passing, key=lambda row: (row["effective_sensitivity"], row["precision"], row["coverage"]), default=None)
    evaluated = None
    if chosen is not None:
        evaluated = summarize(evaluation, lambda row: acoustic_decision(row, feature, chosen["threshold"], require_agreement))
    return {"calibration_curve": rows, "selected_on_calibration": chosen, "evaluation": evaluated}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=CACHE / "eoi-l2-arctic-research")
    parser.add_argument("--observations", type=Path, default=CACHE / "eoi-ifmdd-audit" / "observed-es.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    if any(path.resolve().is_relative_to(root) for path in (args.cache, args.observations)):
        parser.error("Research audio and predictions must remain outside the repository")
    source = args.observations.read_bytes()
    frozen = json.loads(source)
    if frozen.get("decoder") != "beam" or len(frozen["observations"]) != SAMPLE_COUNT * len(SPEAKERS):
        parser.error("Expected the frozen historical IF-MDD beam predictions")
    started = perf_counter()
    rows, duration = collect(args.cache, frozen["observations"])
    calibration = [row for row in rows if row["speaker"] in CALIBRATION]
    evaluation = [row for row in rows if row["speaker"] in EVALUATION]
    if (len(calibration), sum(r["positive"] for r in calibration),
            len(evaluation), sum(r["positive"] for r in evaluation)) != (43, 31, 14, 9):
        raise ValueError("Historical cohort changed")
    baseline = lambda row: row["emitted"] == "S"
    baselines = {name: summarize(group, baseline) for name, group in
                 (("all", rows), ("calibration", calibration), ("evaluation", evaluation))}
    if (baselines["all"]["tp"], baselines["all"]["fp"]) != (37, 2):
        raise ValueError("IF-MDD baseline alignment changed")
    result = {
        "observations_sha256": sha256(source).hexdigest(),
        "calibration_voices": CALIBRATION, "evaluation_voices": EVALUATION,
        "independent_final_validation": False,
        "oracle_uses_annotated_spans": True,
        "inferred_uses_textgrid_canonical_and_ctc_centers": True,
        "inferred_window_iou_median": median([r["overlap"] for r in rows if r["overlap"] is not None]),
        "baseline_ifmdd": baselines,
        "feature_coverage": {feature: {speaker: sum(r["speaker"] == speaker and r[feature] is not None for r in rows)
                                        for speaker in SPEAKERS}
                             for feature in ("oracle_voicing", "inferred_voicing")},
        "results": {feature: {
            "acoustics": fit(calibration, evaluation, feature, False),
            "agreement": fit(calibration, evaluation, feature, True),
        } for feature in ("oracle_voicing", "inferred_voicing")},
        "local_acoustic_runtime_seconds": round(perf_counter() - started, 4),
        "local_audio_duration_seconds": round(duration, 4),
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
