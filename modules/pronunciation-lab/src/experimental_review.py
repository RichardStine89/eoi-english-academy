"""Select a fragment for optional listening, with no scoring or write-back."""

import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

import av
import numpy as np

from lab import SAMPLE_RATE
from phonetics import MAX_SECONDS


_ARPABET_VOWELS = frozenset("AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW".split())
_IPA_VOWEL = frozenset("aeiouɑɒæɐəɛɜɝɞɪɔʊʌ")


class ReviewUnavailable(RuntimeError):
    """The optional offline worker cannot select a fragment."""


def _targets(words: list[dict]) -> list[tuple[int, tuple[dict, dict, dict]]]:
    targets = []
    for index, word in enumerate(words):
        if not word.get("alignment_supported"):
            continue
        if any("z" not in reference for reference in (word.get("reference_ipa_variants") or [])):
            continue
        phones = word.get("aligned_phones") or []
        if [phone["expected_model_phone"] for phone in phones] != word.get("reference_phones"):
            continue
        for left, centre, right in zip(phones, phones[1:], phones[2:]):
            if (centre["expected_model_phone"] == "z"
                    and _IPA_VOWEL.intersection(left["expected_model_phone"])
                    and _IPA_VOWEL.intersection(right["expected_model_phone"])):
                targets.append((index, (left, centre, right)))
    return targets


def _select(targets: list[tuple[int, tuple[dict, dict, dict]]], decoded: list) -> int | None:
    for before, centre, after in zip(decoded, decoded[1:], decoded[2:]):
        if before[0] not in _ARPABET_VOWELS or centre[0] != "S" or after[0] not in _ARPABET_VOWELS:
            continue
        matches = [index for index, expected in targets
                   if all(phone["start_seconds"] <= observed[1] <= phone["end_seconds"]
                          for phone, observed in zip(expected, (before, centre, after), strict=True))]
        if len(matches) == 1:
            return matches[0]
    return None


def _decode(samples: np.ndarray, rate: int) -> list:
    default = Path(tempfile.gettempdir()) / "eoi-ifmdd-audit"
    if os.environ.get("LOCALAPPDATA"):
        installed = Path(os.environ["LOCALAPPDATA"]) / "EOI English Academy" / "Pronunciation Lab" / "IF-MDD"
        if installed.is_dir():
            default = installed
    python = Path(os.environ.get("EOI_IFMDD_PYTHON") or default / "venv" / "Scripts" / "python.exe")
    models = Path(os.environ.get("EOI_IFMDD_MODELS") or default)
    if not python.is_file() or not models.is_dir():
        raise ReviewUnavailable("El entorno local de IF-MDD no está disponible. Usa la escucha manual.")
    if rate != SAMPLE_RATE:
        frame = av.AudioFrame.from_ndarray(samples.astype(np.float32, copy=False)[None, :],
                                           format="fltp", layout="mono")
        frame.sample_rate = rate
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=SAMPLE_RATE)
        frames = resampler.resample(frame) + resampler.resample(None)
        if not frames:
            return []
        samples = np.concatenate([frame.to_ndarray()[0] for frame in frames])
    pcm = samples[:MAX_SECONDS * SAMPLE_RATE].astype("<f4", copy=False).tobytes()
    try:
        response = subprocess.run(
            [str(python.resolve()), "-I", str(Path(__file__).with_name("ifmdd_worker.py")), str(models.resolve())],
            input=pcm, capture_output=True, check=True, timeout=90,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        decoded = json.loads(response.stdout)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        raise ReviewUnavailable("IF-MDD no pudo preparar un fragmento. Usa la escucha manual.") from exc
    if (not isinstance(decoded, list)
            or any(not isinstance(row, list) or len(row) != 2 or not isinstance(row[0], str)
                   or type(row[1]) not in (int, float) or not math.isfinite(row[1]) for row in decoded)):
        raise ReviewUnavailable("IF-MDD devolvió un formato inesperado. Usa la escucha manual.")
    return decoded


def select_fragment(audio: tuple[np.ndarray, int], words: list[dict]) -> int | None:
    samples, rate = audio
    if samples.ndim != 1 or not rate // 4 <= samples.size <= MAX_SECONDS * rate:
        return None
    targets = _targets(words)
    if targets:
        return _select(targets, _decode(samples, rate))
    return None
