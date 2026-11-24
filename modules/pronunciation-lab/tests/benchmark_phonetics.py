"""Small, reproducible human-annotation check for guided English reading.

Run with the lab Python interpreter and --download once, then omit --download
for offline runs with the same cache. Use --prepare-only to fetch the data
before the local model is available. Recordings remain outside the repository.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys
import tempfile
import time
import unicodedata
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parents[1] / "src"
REVISION = "613968e3b0b789fc33936fb5eba1973176ba7d11"
UPSTREAM = f"https://raw.githubusercontent.com/jimbozhang/speechocean762/{REVISION}"
WAV_SET_SHA256 = "87a6cc47b2ae680b944ce25072ca6ee4fd4e4f03be811cb1641da63ae60f2bf6"
WAV_ALL_ANNOTATED_SHA256 = "5969f5b00b1040ca8a9cbf46b5886822bfe5593f61d68848fe4a37605e32b100"
METADATA = {
    "resource/scores.json": "31c847b8ee29d61d8fe338bcbb1d4c4721425f05481d2144ad57cd19ea1159f8",
    "test/wav.scp": "ec911e9319759c73e71ab62dc9cf6a2a00a1d02b7b91a288b39e6d56451e66f3",
    "test/spk2age": "bcc719f23f2352b76f3cec80f12a02f97d775ecfa7b77646be136159caf036d3",
}
REFERENCE_CASES = (
    ("AE", "AH"),
    ("AE", "AH"),
    ("TH", "T"),
    ("TH", "T"),
    ("TH", "S"),
    ("DH", "D"),
    ("Z", "S"),
    ("Z", "S"),
    ("HH", "<DEL>"),
    ("L", "<DEL>"),
    ("F", "<DEL>"),
    ("M", "<DEL>"),
)
IPA = {
    "AE": {"æ"},
    "AH": {"ʌ", "ə"},
    "TH": {"θ"},
    "DH": {"ð"},
    "T": {"t"},
    "D": {"d"},
    "Z": {"z"},
    "S": {"s"},
    "HH": {"h"},
    "L": {"l", "ɫ", "l̴"},
    "F": {"f"},
    "M": {"m"},
}
EVALUATED_WORD = {"no_deviation_detected", "possible_deviation"}


@dataclass(frozen=True)
class Case:
    utterance: str
    speaker: str
    audio_path: str
    words: tuple[str, ...]
    prompt: str
    word_index: int
    canonical: str
    actual: str
    phone_accuracy: float

    @property
    def word(self):
        return self.words[self.word_index]


def _cached_file(cache, relative, download, digest=None):
    path = cache / relative.replace("/", "-")
    if not path.is_file():
        if not download:
            raise FileNotFoundError(f"Falta {relative}. Ejecuta con --download una vez.")
        cap = 12_000_000 if digest else 1_000_000
        with urlopen(f"{UPSTREAM}/{relative}", timeout=40) as response:
            content = response.read(cap + 1)
        if len(content) > cap:
            raise ValueError(f"Archivo de corpus fuera del límite: {relative}")
        if digest and hashlib.sha256(content).hexdigest() != digest:
            raise ValueError(f"SHA-256 inesperado: {relative}")
        if not digest and (content[:4] != b"RIFF" or content[8:12] != b"WAVE"):
            raise ValueError(f"El archivo del corpus no es WAV: {relative}")
        with path.open("xb") as target:
            target.write(content)
    if digest and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        raise ValueError(f"La copia de metadatos tiene otro SHA-256: {relative}")
    return path


def _candidates(cache, download):
    scores, wavs, ages = (
        _cached_file(cache, name, download, digest).read_text(encoding="utf-8-sig")
        for name, digest in METADATA.items()
    )
    metadata = json.loads(scores)
    recordings = dict(line.split(maxsplit=1) for line in wavs.splitlines() if line.strip())
    age_by_speaker = dict(line.split(maxsplit=1) for line in ages.splitlines() if line.strip())
    for utterance, relative in sorted(recordings.items()):
        match = re.fullmatch(r"WAVE/SPEAKER(\d+)/(\d+)\.WAV", relative)
        if match is None or match[2] != utterance:
            raise ValueError(f"Ruta inesperada en test/wav.scp: {relative}")
        speaker = match[1]
        # Keep the evaluation small and limited to adults. Omit the scorer's demo.
        if int(age_by_speaker[speaker]) < 18 or utterance == "014200206":
            continue
        row = metadata[utterance]
        prompt = row["text"]
        words = tuple(word["text"] for word in row["words"])
        if not 3 <= len(words) <= 11 or tuple(re.findall(r"[A-Z]+(?:'[A-Z]+)*", prompt)) != words:
            continue
        for word_index, word in enumerate(row["words"]):
            raw_phones = word["phones"]
            raw_phones = raw_phones.split() if isinstance(raw_phones, str) else raw_phones
            phones = [p.rstrip("012") for p in raw_phones]
            defects = {event["index"]: event["pronounced-phone"] for event in word.get("mispronunciations", [])}
            for index, (phone, score) in enumerate(zip(phones, word["phones-accuracy"], strict=True)):
                if phone not in IPA or phones.count(phone) != 1:
                    continue
                if phone == "AH" and raw_phones[index] == "AH0":
                    continue
                if index in defects:
                    actual = defects[index]
                elif score == 2:
                    actual = phone
                else:
                    continue
                if (phone, actual) in REFERENCE_CASES or actual == phone:
                    yield Case(utterance, speaker, relative, words, prompt, word_index, phone, actual, score)


def choose_cases(cache, download):
    pool = list(_candidates(cache, download))
    chosen = []
    utterances = set()
    speakers = set()
    for canonical, actual in REFERENCE_CASES:
        matches = [
            case for case in pool
            if (case.canonical, case.actual) == (canonical, actual) and case.utterance not in utterances
        ]
        if not matches:
            raise ValueError(f"No hay un caso de referencia para {canonical} → {actual}.")
        chosen_case = min(matches, key=lambda case: (
            case.speaker in speakers, case.phone_accuracy, len(case.words), case.utterance, case.word_index
        ))
        chosen.append(chosen_case)
        utterances.add(chosen_case.utterance)
        speakers.add(chosen_case.speaker)
    for mistake in tuple(chosen):
        matches = [
            case for case in pool
            if case.canonical == case.actual == mistake.canonical and case.utterance not in utterances
        ]
        if not matches:
            raise ValueError(f"No hay un control de referencia para {mistake.canonical}.")
        chosen_case = min(matches, key=lambda case: (
            case.word != mistake.word, case.speaker in speakers, len(case.words), case.utterance, case.word_index
        ))
        chosen.append(chosen_case)
        utterances.add(chosen_case.utterance)
        speakers.add(chosen_case.speaker)
    return chosen


def _phone(value):
    return unicodedata.normalize("NFC", value or "").strip("/[] ").replace("ː", "").replace("͡", "")


def _evaluate(case, evidence):
    expected = IPA[case.canonical]
    rows = evidence.get("words") or []
    if tuple(row.get("expected", "").casefold() for row in rows) != tuple(
        word.casefold() for word in case.words
    ):
        return {
            "outcome": "not_evaluated",
            "reason": evidence.get("reason") or "word_alignment_unavailable",
            "findings": [],
        }
    word = rows[case.word_index]
    if word.get("status") not in EVALUATED_WORD:
        return {"outcome": "not_evaluated", "reason": word.get("status"), "findings": []}
    if sum(_phone(token) in expected for token in word.get("reference_phones") or []) != 1:
        return {"outcome": "not_evaluated", "reason": "reference_phone_incomparable", "findings": []}
    findings = [
        item for item in word.get("findings") or []
        if _phone(item.get("expected")) in expected
    ]
    error = case.actual != case.canonical
    diagnosis = any(
        item.get("kind") == "possible_omission" if case.actual == "<DEL>" else
        item.get("kind") == "substitution" and _phone(item.get("observed")) in IPA[case.actual]
        for item in findings
    ) if error else None
    return {
        "outcome": ("tp" if findings else "fn") if error else ("fp" if findings else "tn"),
        "diagnosis_match": diagnosis,
        "findings": findings,
    }


def _run_engine(cases, paths):
    sys.path.insert(0, str(SRC))
    from acoustics import analyze
    from lab import load_audio
    from phonetics import analyze_phonetics

    rows = []
    for case, path in zip(cases, paths, strict=True):
        samples, rate = load_audio(path)
        quality = analyze(samples, rate)
        start = time.perf_counter()
        evidence = analyze_phonetics(samples, rate, case.prompt, quality)
        elapsed = round(time.perf_counter() - start, 3)
        rows.append({
            "utterance": case.utterance,
            "speaker": case.speaker,
            "word": case.word,
            "canonical": case.canonical,
            "annotated": case.actual,
            "annotation_accuracy": case.phone_accuracy,
            "engine_status": evidence.get("status"),
            "seconds": elapsed,
            **_evaluate(case, evidence),
        })
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=Path(tempfile.gettempdir()) / "eoi-phonetics-public-corpora")
    parser.add_argument("--download", action="store_true", help="Fetch pinned public corpus data once.")
    parser.add_argument("--prepare-only", action="store_true", help="Cache the fixed selection before running the engine.")
    parser.add_argument(
        "--all-annotated", action="store_true",
        help="Include every eligible test error for the fixed contrasts and retain the 12 default controls.",
    )
    args = parser.parse_args()
    cache = args.cache_dir.resolve()
    if cache.is_relative_to(ROOT):
        parser.error("La caché de voces tiene que estar fuera del repositorio.")
    try:
        cache.mkdir(parents=True, exist_ok=True)
        cases = choose_cases(cache, args.download)
        if args.all_annotated:
            cases = [
                case for case in _candidates(cache, args.download) if case.canonical != case.actual
            ] + [case for case in cases if case.canonical == case.actual]
        paths = [_cached_file(cache, case.audio_path, args.download) for case in cases]
        waves = hashlib.sha256(b"".join(hashlib.sha256(path.read_bytes()).digest() for path in paths))
        expected_waves = WAV_ALL_ANNOTATED_SHA256 if args.all_annotated else WAV_SET_SHA256
        if waves.hexdigest() != expected_waves:
            raise ValueError("Las grabaciones de la selección no coinciden con sus huellas de referencia.")
        summary = {
            "source": "https://www.openslr.org/101/",
            "attribution": "Zhang et al. (2021), speechocean762, CC BY 4.0",
            "upstream_revision": REVISION,
            "wav_set_sha256": waves.hexdigest(),
            "design": (
                "Adult official test split. All eligible errors for the fixed contrasts. "
                "Some utterances contribute more than one annotated target. Controls are unchanged."
                if args.all_annotated else
                "Adult official test split. One target phone per utterance, selected by annotation before scoring. "
                "Correct controls require 2.0 and no marked event."
            ),
            "limitation": "Selected and not representative. Mandarin L1 with US-style annotation. The scorer authors have used this corpus. Not an independent validation for British English or Spanish L1.",
            "utterances": len({case.utterance for case in cases}),
            "speakers": len({case.speaker for case in cases}),
            "audio_bytes": sum(path.stat().st_size for path in paths),
            "annotated_errors": sum(case.canonical != case.actual for case in cases),
            "controls": sum(case.canonical == case.actual for case in cases),
        }
        if not args.prepare_only:
            results = _run_engine(cases, paths)
            outcomes = Counter(row["outcome"] for row in results)
            summary["counts"] = {outcome: outcomes[outcome] for outcome in ("tp", "tn", "fp", "fn", "not_evaluated")}
            summary["not_evaluated_annotated_errors"] = sum(
                row["outcome"] == "not_evaluated" and row["canonical"] != row["annotated"] for row in results
            )
            summary["diagnoses_matching_annotation"] = sum(row.get("diagnosis_match") is True for row in results)
            summary["cold_seconds"] = results[0]["seconds"]
            summary["warm_median_seconds"] = statistics.median(row["seconds"] for row in results[1:])
            summary["cases"] = results
        print(json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
