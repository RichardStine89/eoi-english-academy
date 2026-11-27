"""Select paired phonetic rules on cached development data and apply them to NJS."""

import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import gettempdir

import numpy as np

from benchmark_ctc_contrasts import align_ctc, intervals, refine_boundaries, spectral_changes
from benchmark_sibilant_acoustics import ARPA, align_indices, phone, summarize, load_audio


PAIRS = (("Z", "S"), ("DH", "D"), ("IH", "IY"))
FEATURES = ("neural", "ctc_spectral", "cupe")
TRAIN = {"EBVS", "ERMS"}
CALIBRATION = "MBMPS"
TRANSFER = "NJS"
CUTS = (.35, .50, .65, .80, .90)
ADVANCED = (.80, .95, .90)
ADVISORY = (.60, .90, .80)


def write_new(path, result):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")


def prepare(work):
    # The earlier acoustic extractor stays in the local research cache. No model inference is repeated.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".cache"))
    from multicontrast_acoustics import CORPUS, PREDICTIONS, VOWELS, frames, measure
    from ifmdd_compare import l2_cases

    phase4 = Path(gettempdir()) / "eoi-mdd-phase4"
    historical = json.loads((phase4 / "multicontrast-acoustics.json").read_bytes())
    prediction_data = PREDICTIONS.read_bytes()
    if sha256(prediction_data).hexdigest() != historical["observations_sha256"]:
        raise ValueError("IF-MDD observations changed")
    observed = json.loads(prediction_data)["observations"]
    cupe_data = (phase4 / "cupe-es-windows.json").read_bytes()
    cupe = json.loads(cupe_data)["observations"]
    emission_path = phase4 / "ifmdd-es-frames.npz"
    source_hashes = {"ifmdd": sha256(prediction_data).hexdigest(), "cupe": sha256(cupe_data).hexdigest(),
                     "emissions": sha256(emission_path.read_bytes()).hexdigest()}
    if source_hashes["cupe"] != "a54325625470e4e67f295c4d2f76fc6e40fe294a55c410500ba45beab7eea895" or \
       source_hashes["emissions"] != "350af5bfd7da928dcd88a98cafecabc9db8de97219f56be9a5444eeb506080be":
        raise ValueError("Cached CUPE or CTC boundaries changed")
    rows = defaultdict(list)
    audio_hashes = {}
    for speaker in sorted(TRAIN | {CALIBRATION, TRANSFER}):
        manifest = json.loads((CORPUS / speaker / "manifest.json").read_bytes())
        audio_hashes.update({f"{speaker}/{item['id']}":item["sha256"]["wav"] for item in manifest})
    with np.load(emission_path, allow_pickle=False) as emissions:
        vocab = {phone(label): index for index, label in enumerate(emissions["phone_tags"].tolist())}
        step, offset = float(emissions["step"]), float(emissions["offset"])
        for key, canonical, targets, _ in l2_cases(CORPUS):
            speaker = key.split("/")[0]
            if canonical != cupe[key]["canonical"]:
                raise ValueError("Cached canonical sequences disagree")
            path = CORPUS / f"{key}.wav"
            if sha256(path.read_bytes()).hexdigest() != audio_hashes[key]:
                raise ValueError("Cached recording does not match its manifest")
            audio, rate = load_audio(path)
            duration = len(audio) / rate
            if rate != 16000 or abs(duration - observed[key]["duration_seconds"]) > .0001:
                raise ValueError("Audio does not match frozen observations")
            tokens = observed[key]["phones"]
            labels = [phone(value["phone"]) for value in tokens]
            lexical = [i for i, name in enumerate(labels) if name in ARPA]
            matched = align_indices(canonical, [labels[i] for i in lexical])
            runs = align_ctc(emissions[key], [vocab[value] for value in labels])
            if runs is None:
                raise ValueError("Cached sequence has no CTC path")
            raw = intervals(runs, offset, step, duration)
            times, change = spectral_changes(audio, rate)
            spectral = refine_boundaries(raw, labels, times, change)
            acoustic = frames(audio, rate)
            for slot, expected, gold, _, _ in targets:
                for pair in PAIRS:
                    if pair[0] != expected or gold not in pair:
                        continue
                    index = lexical[matched[slot]] if matched[slot] is not None else None
                    current = labels[index] if index is not None else None
                    row = {"speaker":speaker, "positive":gold == pair[1],
                           "beam":None if current is None else current == pair[1], "neural":None}
                    if index is not None:
                        mass = tokens[index]["local_posteriors"]
                        margin = np.log(mass[pair[1].lower()] + 1e-6) - np.log(mass[expected.lower()] + 1e-6)
                        row["neural"] = [float(current == pair[1]), float(current == expected), float(margin)]
                    left = slot > 0 and canonical[slot-1] in VOWELS
                    right = slot+1 < len(canonical) and canonical[slot+1] in VOWELS
                    cupe_window = cupe[key]["intervals"].get(str(slot))
                    ctc_window = spectral[index:index+2] if index is not None else None
                    row["ctc_spectral"] = measure(acoustic, ctc_window, expected, left, right)
                    row["cupe"] = measure(acoustic, cupe_window, expected, left, right)
                    rows["->".join(pair)].append(row)
    for name in ("development", "transfer"):
        payload = {key:[row for row in values if (row["speaker"] == TRANSFER) == (name == "transfer")]
                   for key, values in rows.items()}
        write_new(work / f"{name}.json", {"sources":source_hashes, "rows":payload})


def sigmoid(value):
    return 1 / (1 + np.exp(-np.clip(value, -30, 30)))


def fit(rows, feature):
    usable = [r for r in rows if r[feature] is not None]
    if {r["positive"] for r in usable} != {True, False}:
        raise ValueError(f"Training lacks both labels for {feature}")
    x = np.asarray([r[feature] for r in usable], dtype=float)
    y = np.asarray([r["positive"] for r in usable], dtype=float)
    mean, std = x.mean(axis=0), np.maximum(x.std(axis=0), 1e-6)
    design = np.column_stack((np.ones(len(x)), (x - mean) / std))
    regularization = np.diag([0., *np.ones(len(mean))])
    coef = np.zeros(design.shape[1])
    for _ in range(30):
        prob = sigmoid(design @ coef)
        grad = design.T @ (prob - y) + regularization @ coef
        hessian = design.T @ (np.maximum(prob * (1-prob), 1e-8)[:, None] * design) + regularization
        update = np.linalg.solve(hessian, grad)
        coef -= update
        if np.linalg.norm(update) < 1e-8:
            break
    return {"mean":mean.tolist(), "std":std.tolist(), "coef":coef.tolist()}


def scores(row, models):
    result = {"beam":row["beam"]}
    for name, model in models.items():
        vector = row[name]
        beta = np.asarray(model["coef"])
        result[name] = (float(sigmoid(beta[0] + ((vector-np.asarray(model["mean"]))/model["std"]) @ beta[1:]))
                        if vector is not None else None)
    return result


def decision(value, rule):
    family, feature, cut, mixing = rule
    score = value[feature]
    if family == "specialist":
        return score >= cut if score is not None else None
    if family == "vote":
        neural = value["neural"]
        return mixing*neural+(1-mixing)*score >= cut if neural is not None and score is not None else None
    beam = value["beam"]
    if beam is not True:
        return beam
    if score is None:
        return None
    if score >= cut:
        return True
    return False if mixing and score <= .20 else None


def qualifies(metrics, thresholds):
    names = ("effective_sensitivity", "precision", "coverage")
    return all(metrics[name] is not None and metrics[name] >= floor for name, floor in zip(names, thresholds))


def rules():
    for feature in FEATURES:
        for cut in CUTS:
            yield ("specialist", feature, cut, 0.)
    for feature in ("ctc_spectral", "cupe"):
        for cut in CUTS:
            for weight in (.25, .50, .75):
                yield ("vote", feature, cut, weight)
        for cut in (.40, .60, .80):
            for reject in (False, True):
                yield ("cascade", feature, cut, reject)


def rank(metrics):
    return (qualifies(metrics,ADVANCED), qualifies(metrics,ADVISORY), metrics["effective_f1"] or 0,
            metrics["coverage"] or 0, metrics["precision"] or 0)


def select(work):
    data_file = work / "development.json"
    data = data_file.read_bytes()
    package = json.loads(data)
    frozen = {}
    for contrast, rows in package["rows"].items():
        if {row["speaker"] for row in rows} != TRAIN | {CALIBRATION}:
            raise ValueError("Development contains an unexpected voice")
        training = [row for row in rows if row["speaker"] in TRAIN]
        calibration = [row for row in rows if row["speaker"] == CALIBRATION]
        models = {feature:fit(training, feature) for feature in FEATURES}
        prepared = [(row, scores(row,models)) for row in calibration]
        candidates = defaultdict(list)
        for rule in rules():
            values = [{**row,"decision":decision(score,rule)} for row, score in prepared]
            candidates[rule[0]].append({"rule":rule,"metrics":summarize(values,lambda row:row["decision"])})
        frozen[contrast] = {"models":models,"selected":{key:max(values,key=lambda value:rank(value["metrics"]))
                                                         for key,values in candidates.items()}}
    write_new(work / "frozen-selection.json", {
        "development_sha256":sha256(data).hexdigest(), "sources":package["sources"],
        "training":sorted(TRAIN),"calibration":CALIBRATION,"contrasts":frozen,
    })


def evaluate(work):
    selection = (work / "frozen-selection.json").read_bytes()
    frozen = json.loads(selection)
    package = json.loads((work / "transfer.json").read_bytes())
    if package["sources"] != frozen["sources"]:
        raise ValueError("The two stages do not share the same frozen inputs")
    result = {}
    for contrast, rows in package["rows"].items():
        if {row["speaker"] for row in rows} != {TRANSFER}:
            raise ValueError("Expected only NJS at transfer")
        selected = frozen["contrasts"][contrast]
        prepared = [(row, scores(row,selected["models"])) for row in rows]
        report = {"beam":summarize(rows,lambda row:row["beam"])}
        for family, candidate in selected["selected"].items():
            outcomes = [{**row,"decision":decision(value,candidate["rule"])} for row,value in prepared]
            metrics = summarize(outcomes,lambda row:row["decision"])
            report[family] = {"rule":candidate["rule"], "calibration":candidate["metrics"],
                              "transfer":metrics, "passes_advisory":qualifies(metrics,ADVISORY),
                              "passes_advanced":qualifies(metrics,ADVANCED)}
        result[contrast] = report
    write_new(work / "comparison.json", {"selection_sha256":sha256(selection).hexdigest(),
                                         "transfer":TRANSFER,"independent":False,"results":result})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage",choices=("prepare","select","evaluate"))
    parser.add_argument("--workdir",type=Path,required=True)
    args = parser.parse_args()
    if args.workdir.resolve().is_relative_to(Path(__file__).resolve().parents[3]):
        parser.error("Keep research features outside Git")
    args.workdir.mkdir(parents=True,exist_ok=True)
    {"prepare":prepare,"select":select,"evaluate":evaluate}[args.stage](args.workdir)
