"""Conservative, local phonetic evidence for a known English prompt."""

from functools import lru_cache
import math
import os
import re

import numpy as np
import parselmouth

from phonetic_model import CACHE, FILES, MODEL, MODEL_DIR, REVISION, WEIGHTS, verified


ENGINE = "Pronunciada 1.1.0"
MODEL_LABEL = f"ZIPA {MODEL} int8"
MAX_SECONDS = 30
MAX_WORDS = 65

# Independent teaching references for the first contrast exercises. The model uses CMUdict.
BRITISH_IPA = {
    "ship": "ʃɪp", "sheep": "ʃiːp", "live": None, "leave": "liːv",
    "full": "fʊl", "fool": "fuːl", "three": "θriː", "tree": "triː",
    "very": "ˈveri", "berry": "ˈberi", "hat": "hæt", "hut": "hʌt",
    "bad": "bæd", "bed": "bed", "hello": "həˈləʊ", "name": "neɪm",
    "guide": "ɡaɪd", "spain": "speɪn", "spanish": "ˈspænɪʃ",
    "meet": "miːt", "nice": "naɪs",
}
BRITISH_VARIANTS = {"with": ["wɪθ", "wɪð"], "either": ["ˈaɪðə", "ˈiːðə"],
                    "neither": ["ˈnaɪðə", "ˈniːðə"], "route": ["ruːt"]}
CONTRASTS = (
    ({"ɪ", "i"}, "ship/sheep o live/leave con live como verbo"),
    ({"ʊ", "u"}, "full/fool"),
    ({"æ", "ʌ"}, "hat/hut"),
    ({"æ", "ɛ"}, "bad/bed"),
    ({"b", "v"}, "berry/very"),
    ({"θ", "t"}, "three/tree"),
    ({"θ", "s"}, "thin/sin"),
    ({"ð", "d"}, "they/day"),
    ({"s", "z"}, "sip/zip"),
)
LIMITATIONS = [
    "Alineación con el guion y alternativas del modelo CTC; no hay ASR ni confirmación independiente de palabras.",
    "CMUdict es estadounidense. Se filtran contrastes sensibles al dialecto; no hay calibración británica local.",
    "Las probabilidades son indicadores del motor. Una hipótesis requiere escucha y no es una calificación.",
    "La secuencia libre de CTC se observa en la ventana alineada. Sus indicios de revisión son exploratorios y no se puntúan.",
    "Inserciones, inteligibilidad, enlace y corrección de acento, ritmo y entonación no se evalúan automáticamente.",
]


@lru_cache(maxsize=1)
def _scorer():
    if not all(verified(MODEL_DIR / name, *details) for name, details in FILES.items()):
        raise FileNotFoundError("Ejecuta Instalar.cmd para verificar el modelo fonético.")
    # Scorer exposes these documented upstream overrides. Preverified local files avoid lazy downloads.
    os.environ["PRONUNCIADA_CACHE"] = str(CACHE)
    os.environ["PRONUNCIADA_BACKBONE"] = str(MODEL_DIR / WEIGHTS)
    from pronunciada import Scorer

    return Scorer("en", model=MODEL, precision="int8", threads=4, cache_size=1, delivery=False)


def _result(status: str, reason: str | None = None) -> dict:
    return {"status": status, "reason": reason, "engine": ENGINE, "model": MODEL_LABEL,
            "model_revision": REVISION, "acoustic_reference": "English ZIPA + CMUdict estadounidense",
            "words": [], "temporal": None, "limitations": LIMITATIONS.copy()}


def _probability(value) -> float | None:
    if value is None or not math.isfinite(value) or not 0 <= value <= 1:
        return None
    return round(float(value), 3)


def _interval(start: float, end: float, duration: float) -> tuple[float | None, float | None]:
    if math.isfinite(start) and math.isfinite(end) and 0 <= start < min(end, duration):
        return round(float(start), 3), round(min(float(end), duration), 3)
    return None, None


def _symbol(phone: str) -> str:
    return phone.replace("ː", "").replace("ɡ", "g").replace("˞", "")


def _finding(item: dict, word, duration: float) -> dict | None:
    kind = item["kind"]
    target, heard = item.get("expected_ipa"), item.get("heard_ipa")
    confidence = _probability(item.get("confidence"))
    strength = _probability(item.get("error_prob"))
    if not target or confidence is None or strength is None or strength < 0.55:
        return None
    start, end = _interval(item["start"], item["end"], duration)
    if kind == "substitution" and heard and start is not None:
        pair = {_symbol(target), _symbol(heard)}
        contrast = next((example for phones, example in CONTRASTS if phones == pair), None)
        if contrast is None:
            return None
        recommendation = f"Escucha la palabra y practica {contrast}. Después repite la frase."
    elif kind == "missing" and target in {"h", "l", "f", "m", "p", "k", "s", "z"}:
        if target == "h" and word.text.casefold() in {"he", "his", "him", "her", "have", "has", "had"}:
            return None
        kind = "possible_omission"
        heard = None
        recommendation = f"Escucha la palabra completa y repítela prestando atención a /{target}/."
    else:
        return None
    return {"kind": kind, "expected": target, "observed": heard, "confidence": confidence,
            "engine_error_probability": strength, "start_seconds": start, "end_seconds": end,
            "recommendation": recommendation}


def _word_evidence(word, items: list[dict], duration: float) -> dict:
    start, end = _interval(word.start, word.end, duration)
    presence = _probability(word.present_prob)
    phone_prob = [_probability(p.prob) for p in word.phones]
    findings = []
    supporting_phones = sum(prob is not None and prob >= 0.50 for prob in phone_prob)
    enough_support = bool(phone_prob) and supporting_phones >= math.ceil(len(phone_prob) / 2)
    sufficient = (start is not None and end - start >= 0.07 and not word.omitted
                  and (presence is None or presence >= 0.55) and enough_support)
    if sufficient:
        findings = [finding for item in items if (finding := _finding(item, word, duration)) is not None]
    status = "insufficient_evidence"
    confidence = None
    if findings:
        status = "possible_deviation"
        confidence = max(finding["confidence"] for finding in findings)
    elif sufficient and all(p is not None and p >= 0.60 for p in phone_prob) and phone_prob:
        status = "no_deviation_detected"
        confidence = min(phone_prob)
    return {
        "expected": word.text, "recognized": None, "start_seconds": start, "end_seconds": end,
        "expected_ipa": BRITISH_IPA.get(word.text.casefold()),
        "reference_ipa_variants": BRITISH_VARIANTS.get(word.text.casefold()),
        "reference_phones": [p.ipa for p in word.phones],
        "observed_phones": [finding["observed"] for finding in findings if finding["observed"]] or None,
        "status": status, "confidence": confidence, "model_presence": presence, "findings": findings,
        "alignment_supported": sufficient, "free_ctc": None,
        "syllables": [{"start_seconds": bounds[0], "end_seconds": bounds[1],
                       "expected_model_stress": sy.stress_expected,
                       "model_stress_support": _probability(sy.stress_prob)}
                      for sy in word.syllables if (bounds := _interval(sy.start, sy.end, duration))[0] is not None],
        "aligned_phones": [
            {"expected_model_phone": phone.ipa, "start_seconds": bounds[0], "end_seconds": bounds[1],
             "duration_seconds": round(bounds[1] - bounds[0], 3), "model_support": _probability(phone.prob)}
            for phone in word.phones if (bounds := _interval(phone.start, phone.end, duration))[0] is not None
        ],
    }


def _unique_edit(expected: list[str], decoded: list[str], word: str = "") -> dict | None:
    """Surface one unambiguous edit for listening, without treating it as an error."""
    if min(len(expected), len(decoded)) < 2 or max(len(expected), len(decoded)) < 3:
        return None
    canon = [*map(_symbol, expected)]
    heard = [*map(_symbol, decoded)]
    if "".join(heard) in {_symbol(variant.replace("ˈ", "")) for variant in BRITISH_VARIANTS.get(word, [])}:
        return None
    if len(canon) == len(heard):
        edits = [(a, b) for a, b in zip(canon, heard) if a != b]
        if len(edits) == 1 and any(set(edits[0]) == pair for pair, _ in CONTRASTS):
            return {"kind": "substitution", "expected": edits[0][0], "observed": edits[0][1]}
    elif len(heard) + 1 == len(canon):
        edits = [x for i, x in enumerate(canon) if canon[:i] + canon[i + 1:] == heard]
        if len(edits) == 1 and edits[0] in {"h", "l", "f", "m", "p", "k", "s", "z"}:
            if word not in {"he", "his", "him", "her", "have", "has", "had"}:
                return {"kind": "possible_omission", "expected": edits[0], "observed": None}
    elif len(canon) + 1 == len(heard):
        edits = [x for i, x in enumerate(heard) if heard[:i] + heard[i + 1:] == canon]
        if len(edits) == 1 and edits[0] in {"ə", "ɪ", "ɛ"}:
            return {"kind": "insertion", "expected": None, "observed": edits[0]}
    return None


def _add_free_ctc(words: list[dict], result, duration: float) -> None:
    # Pronunciada 1.1.0 stores its free greedy CTC path with the forced-alignment evidence.
    cache = getattr(result, "_pronunciada", {}) or {}
    alignment = cache.get("ev")
    if alignment is None or not alignment.free_tokens:
        return
    # ZIPA has a 20 ms output step and 30 ms initial offset for segment starts.
    tokens = [(symbol, *_interval(a * 0.02 + 0.03, b * 0.02 + 0.03, duration))
              for symbol, a, b in alignment.free_tokens]
    for word in words:
        if not word["alignment_supported"]:
            continue
        start, end = word["start_seconds"], word["end_seconds"]
        within = [{"phone": phone, "start_seconds": a, "end_seconds": b}
                  for phone, a, b in tokens if a is not None and start <= (a + b) / 2 < end]
        if not within:
            continue
        hit = _unique_edit(word["reference_phones"], [p["phone"] for p in within], word["expected"].casefold())
        word["free_ctc"] = {"phones": within, "review_candidate": hit, "confidence": None}


def _temporal(words: list[dict], samples: np.ndarray, rate: int) -> dict | None:
    usable = [word for word in words if word["status"] in {"possible_deviation", "no_deviation_detected"}]
    if not usable:
        return None
    try:
        pitch = parselmouth.Sound(samples, sampling_frequency=rate).to_pitch_ac(
            time_step=0.01, pitch_floor=65, pitch_ceiling=550, voicing_threshold=0.60,
        )
    except parselmouth.PraatError:
        pitch = None
    for word in usable:
        start, end = word["start_seconds"], word["end_seconds"]
        if pitch is not None:
            frames = pitch.xs()
            frequency = pitch.selected_array["frequency"]
            selected = frequency[(frames >= start) & (frames < end) & (frequency > 0)]
            word["pitch_median_hz"] = round(float(np.median(selected)), 1) if selected.size >= 4 else None
        segment = samples[round(rate * start):round(rate * end)].astype(np.float64)
        rms = float(np.sqrt(np.mean(segment**2))) if segment.size else 0
        word["rms_dbfs"] = round(20 * math.log10(rms), 2) if rms > 0 else None
    gaps = [round(b["start_seconds"] - a["end_seconds"], 3) for a, b in zip(words, words[1:])
            if a in usable and b in usable and b["start_seconds"] - a["end_seconds"] >= 0.2]
    return {"aligned_words": len(usable), "interword_gaps_seconds": gaps,
            "speaking_rate_wpm": None, "intonation_rating": None}


def analyze_phonetics(samples: np.ndarray, rate: int, text: str | None, quality: dict) -> dict:
    if not text:
        return _result("not_evaluated", "Hace falta un texto de referencia para el cotejo fonético.")
    duration = len(samples) / rate
    if duration > MAX_SECONDS or len(re.findall(r"\b\w+\b", text)) > MAX_WORDS:
        return _result("not_evaluated", "Divide la actividad en fragmentos de hasta 30 s y 65 palabras.")
    if quality.get("status") != "measured" or quality.get("quality", {}).get("status") == "unusable":
        return _result("insufficient_evidence", "La señal no permite evaluar la pronunciación.")
    try:
        result = _scorer().score((samples, rate), text)
        if result.audio and result.audio.get("retry_recommended"):
            if set(result.audio.get("issues", ())) & {"clipped", "too_noisy", "too_short", "too_quiet", "mostly_silence"}:
                return _result("insufficient_evidence", "El motor detecta una toma débil, breve o con ruido para el texto.")
        items = result.coaching(sensitivity="careful", miscues=True, delivery=False)
    except (ValueError, FloatingPointError):
        return _result("insufficient_evidence", "El modelo no pudo alinear esta toma con el guion.")
    except Exception:
        # The third-party engine may raise its own runtime errors. Preserve the acoustic report.
        return _result("not_evaluated", "El motor fonético local no está disponible. Ejecuta Instalar.cmd.")
    per_word = {}
    for item in items:
        per_word.setdefault(item["word_index"], []).append(item)
    evidence = _result("analyzed")
    evidence["words"] = [_word_evidence(word, per_word.get(i, []), duration) for i, word in enumerate(result.words)]
    supported = sum(word["status"] != "insufficient_evidence" for word in evidence["words"])
    if len(evidence["words"]) >= 3 and supported < len(evidence["words"]) / 2:
        evidence["reason"] = "El sonido no sostiene suficientemente la correspondencia general con el guion."
        evidence["status"] = "insufficient_evidence"
        for word in evidence["words"]:
            word.update(status="insufficient_evidence", confidence=None, findings=[], observed_phones=None)
        return evidence
    evidence["temporal"] = _temporal(evidence["words"], samples, rate)
    if evidence["temporal"] is None:
        evidence["status"] = "insufficient_evidence"
        evidence["reason"] = "Ninguna palabra obtuvo evidencia suficiente para interpretar el cotejo."
    else:
        _add_free_ctc(evidence["words"], result, duration)
    return evidence
