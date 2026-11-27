"""Compare frozen CTC segmentation and directed alternatives on cached annotated audio."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re
import sys
from tempfile import gettempdir

import numpy as np

from benchmark_l2_arctic import SAMPLE_COUNT, SPEAKERS, targets, tiers
from benchmark_sibilant_acoustics import ARPA, align_indices, inferred_window, phone

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lab import load_audio


CONTRASTS = (("Z", "S"), ("DH", "D"), ("IH", "IY"), ("TH", "T"), ("TH", "S"),
             ("B", "V"), ("UH", "UW"), ("AE", "AH"))
VOWELS = frozenset("AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW".split())
BLANK = 0


def ctc_states(sequences):
    """Insert blank states and allow skips only to unequal lexical labels."""
    states = np.zeros((len(sequences), 2 * len(sequences[0]) + 1), dtype=np.int64)
    states[:, 1::2] = sequences
    skips = np.zeros_like(states, dtype=bool)
    skips[:, 3::2] = states[:, 3::2] != states[:, 1:-2:2]
    return states, skips


def log_mass(log_frames, sequences):
    states, skips = ctc_states(sequences)
    scores = np.full(states.shape, -np.inf)
    scores[:, 0] = 0
    for frame in log_frames:
        advances = np.roll(scores, 1, axis=1)
        advances[:, :1] = -np.inf
        jumps = np.where(skips, np.roll(scores, 2, axis=1), -np.inf)
        scores = np.logaddexp(np.logaddexp(scores, advances), jumps) + frame[states]
    return np.logaddexp(scores[:, -1], scores[:, -2])


def align_ctc(log_frames, sequence):
    states, skips = ctc_states([sequence])
    states, skips = states[0], skips[0]
    scores = np.full(states.shape, -np.inf)
    scores[0] = 0
    history = np.empty((len(log_frames), len(states)), dtype=np.int8)
    columns = np.arange(len(states))
    for i, frame in enumerate(log_frames):
        advances = np.r_[-np.inf, scores[:-1]]
        jumps = np.where(skips, np.roll(scores, 2), -np.inf)
        options = np.stack((scores, advances, jumps))
        history[i] = options.argmax(axis=0)
        scores = options[history[i], columns] + frame[states]
    state = len(states) - (1 if scores[-1] >= scores[-2] else 2)
    if not np.isfinite(scores[state]):
        return None
    assignment = np.empty(len(log_frames), dtype=np.int64)
    for i in range(len(log_frames) - 1, -1, -1):
        assignment[i] = state
        state -= history[i, state]
    return [np.flatnonzero(assignment == 2 * i + 1) for i in range(len(sequence))]


def intervals(runs, offset, step, duration):
    first = np.array([run[0] for run in runs]) * step + offset
    last = np.array([run[-1] for run in runs]) * step + offset
    splits = (last[:-1] + first[1:]) / 2
    return np.r_[max(0, first[0] - step / 2), splits, min(duration, last[-1] + step / 2)]


def spectral_changes(samples, rate):
    """Independent broadband spectral change, on 10 ms centers and 20 ms windows."""
    length, hop = round(.020 * rate), round(.010 * rate)
    waveform = np.lib.stride_tricks.sliding_window_view(samples, length)[::hop]
    powers = np.abs(np.fft.rfft(waveform * np.hanning(length), axis=1)) ** 2
    freq = np.fft.rfftfreq(length, 1 / rate)
    edges = (80, 350, 1500, 3000, 7500)
    bands = np.stack([powers[:, (freq >= lo) & (freq < hi)].sum(axis=1)
                      for lo, hi in zip(edges, edges[1:])], axis=1)
    total = bands.sum(axis=1)
    feature = np.sqrt(bands / (total[:, None] + 1e-9))
    energy = np.log(np.maximum(total, total.max() * .00001 + 1e-9))
    flux = (np.linalg.norm(feature[2:] - feature[:-2], axis=1)
            + .12 * np.minimum(3, np.abs(energy[2:] - energy[:-2])))
    return (np.arange(1, len(waveform) - 1) * hop + length / 2) / rate, flux


def refine_boundaries(boundaries, labels, times, flux):
    refined = boundaries.copy()
    for slot, (left, right) in enumerate(zip(labels, labels[1:]), 1):
        if (left in VOWELS) == (right in VOWELS) or "SIL" in (left, right):
            continue
        center = boundaries[slot]
        minimum = max(center - .030, refined[slot - 1] + .020)
        maximum = min(center + .030, boundaries[slot + 1] - .020)
        candidates = (times >= minimum) & (times <= maximum)
        if candidates.any():
            points = times[candidates]
            refined[slot] = points[np.argmax(flux[candidates] - 10 * np.abs(points - center))]
    return refined


def read_annotation(file):
    grid = tiers(file.read_text(encoding="utf-8-sig"))
    words = [(start, end) for start, end, value in grid["words"] if re.fullmatch(r"[a-zA-Z']+", value)]
    selected = {(s, e): kind for s, e, _, _, kind in targets(grid["phones"])}
    canonical, scored = [], []
    for start, end, name in grid["phones"]:
        labels = [phone(value) for value in name.split(",")]
        expected = labels[0]
        if expected not in ARPA:
            continue
        kind = selected.get((start, end))
        if kind and any(lo <= (start + end) / 2 < hi for lo, hi in words):
            canonical_actual = expected if kind == "control" else labels[1] if kind == "substitution" else "<DEL>"
            scored.append((len(canonical), expected, canonical_actual, start, end))
        canonical.append(expected)
    return canonical, scored


def span_metrics(predicted, gold):
    left, right = predicted
    start, stop = gold
    union = max(right, stop) - min(left, start)
    iou = max(0, min(right, stop) - max(left, start)) / union
    return (abs(left - start) * 1000, abs(right - stop) * 1000, iou)


def summary(rows):
    counts = Counter(rows)
    tp, fp = counts[True, True], counts[False, True]
    positives = sum(count for (positive, _), count in counts.items() if positive)
    abstain = counts[True, None] + counts[False, None]
    return {"positives": positives, "controls": len(rows)-positives, "tp": tp, "fp": fp,
            "false_negatives_effective": positives-tp, "abstentions": abstain,
            "precision": tp/(tp+fp) if tp+fp else None,
            "sensitivity": tp/positives if positives else None,
            "coverage": (len(rows)-abstain)/len(rows) if rows else None}


def run(corpus, observations, emission_file):
    bounds = defaultdict(list)
    contrast_trials = defaultdict(list)
    span_counts = Counter()
    with np.load(emission_file, allow_pickle=False) as emissions:
        tags = [phone(value) for value in emissions["phone_tags"].tolist()]
        offset, step = float(emissions["offset"]), float(emissions["step"])
        if len(set(tags)) != len(tags) or tags[BLANK] != "<BLANK>" or not ARPA <= set(tags):
            raise ValueError("Unexpected or incomplete CTC vocabulary")
        vocab = {label: i for i, label in enumerate(tags)}
        for speaker in SPEAKERS:
            folder = corpus / speaker
            manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
            if len(manifest) != SAMPLE_COUNT:
                raise ValueError("Research cohort changed")
            for entry in manifest:
                name = entry["id"]
                key = f"{speaker}/{name}"
                audio = folder / f"{name}.wav"
                label_file = folder / f"{name}.TextGrid"
                for path, kind in ((audio, "wav"), (label_file, "TextGrid")):
                    if sha256(path.read_bytes()).hexdigest() != entry["sha256"][kind]:
                        raise ValueError("Cached input does not match its manifest")
                samples, rate = load_audio(audio)
                duration = len(samples) / rate
                canonical, items = read_annotation(label_file)
                clip = observations[key]
                log_frames = emissions[key]
                finite = np.isfinite(log_frames).all()
                if not finite or list(log_frames.shape) != clip["shape"][1:] or abs(duration - clip["duration_seconds"]) > .0001:
                    raise ValueError("Audio, observations, and emissions disagree")
                labels = [phone(token["phone"]) for token in clip["phones"]]
                sequence = [vocab[label] for label in labels]
                centers = [token["center_seconds"] for token in clip["phones"]]
                lexical = [i for i, label in enumerate(labels) if label in ARPA]
                assignment = align_indices(canonical, [labels[i] for i in lexical])
                inferred = align_ctc(log_frames, sequence)
                if inferred is None:
                    raise ValueError("Frozen CTC hypothesis does not have a finite path")
                raw = intervals(inferred, offset, step, duration)
                times, flux = spectral_changes(samples, rate)
                refined = refine_boundaries(raw, labels, times, flux)
                marginals, trial_keys = [], []
                for pos, expected, actual, start, end in items:
                    slot = lexical[assignment[pos]] if assignment[pos] is not None else None
                    split = "njs" if speaker == "NJS" else "ebvs_erms_mbmps"
                    category = "vowels" if expected in VOWELS else "consonants"
                    if actual != "<DEL>":
                        for group in ("all", split):
                            span_counts[group, category, "annotated"] += 1
                        if slot is not None and labels[slot] == actual:
                            windows = {"beam_centers": inferred_window(centers, slot, duration),
                                       "ctc_viterbi": raw[slot:slot+2], "ctc_spectral": refined[slot:slot+2]}
                            for group in ("all", split):
                                for method, window in windows.items():
                                    bounds[group, category, method].append(span_metrics(window, (start, end)))
                    for ref, alternative in CONTRASTS:
                        if expected != ref or actual not in (ref, alternative):
                            continue
                        direction = f"{ref}->{alternative}"
                        positive = actual == alternative
                        beam = labels[slot] == alternative if slot is not None else None
                        if slot is None:
                            contrast_trials[direction].append((split, positive, beam, None))
                            continue
                        a, b = sequence.copy(), sequence.copy()
                        a[slot], b[slot] = vocab[ref], vocab[alternative]
                        marginals.extend((a, b))
                        trial_keys.append((direction, split, positive, beam))
                if marginals:
                    masses = log_mass(log_frames, marginals).reshape(-1, 2)
                    for (direction, split, positive, beam), (expected_mass, alternate_mass) in zip(trial_keys, masses, strict=True):
                        alternative_supported = (bool(alternate_mass > expected_mass)
                                                 if np.isfinite([expected_mass, alternate_mass]).all() else None)
                        contrast_trials[direction].append((split, positive, beam, alternative_supported))

    boundaries = []
    for (split, category, method), rows in sorted(bounds.items()):
        lo, hi, iou = np.median(rows, axis=0)
        boundaries.append({"split": split, "category": category, "method": method, "compared": len(rows),
                           "annotated": span_counts[split, category, "annotated"],
                           "median_start_error_ms": lo, "median_end_error_ms": hi, "median_iou": iou})
    directed = {}
    for ref, alternative in CONTRASTS:
        direction = f"{ref}->{alternative}"
        rows = contrast_trials[direction]
        directed[direction] = {group: {
            "beam": summary([(y, beam) for split, y, beam, _ in rows if split == group or group == "all"]),
            "ctc_likelihood": summary([(y, mass) for split, y, _, mass in rows if split == group or group == "all"]),
        } for group in ("all", "ebvs_erms_mbmps", "njs")}
    return {"boundaries": boundaries, "directed": directed,
            "limitations": "Retrospective. Annotated canonical transcript. Measured boundaries condition on matching the annotated phone. No threshold fitted."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=Path(gettempdir()) / "eoi-l2-arctic-research")
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--emissions", type=Path, required=True)
    args = parser.parse_args()
    frozen = json.loads(args.observations.read_text(encoding="utf-8-sig"))
    if frozen["decoder"] != "beam" or len(frozen["observations"]) != len(SPEAKERS) * SAMPLE_COUNT:
        parser.error("Expected the full historical beam observations")
    result = run(args.corpus, frozen["observations"], args.emissions)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
