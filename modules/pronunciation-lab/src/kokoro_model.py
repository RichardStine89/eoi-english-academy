"""Synthesize an offline British practice model with verified Kokoro assets."""

import ctypes
from functools import lru_cache
import json
from pathlib import Path
import re
import shutil
from tempfile import NamedTemporaryFile, gettempdir
from textwrap import wrap
from threading import Lock
from urllib.request import urlopen

import numpy as np

from phonetic_model import verified


REPOSITORY = "onnx-community/Kokoro-82M-v1.0-ONNX"
REVISION = "a70f0e45c1cc0df9abdfbfa0f6dee9073579ee99"
VOICE = "bf_emma"
MODEL_DIR = Path(__file__).resolve().parents[1] / ".cache" / "kokoro"
SAMPLE_RATE = 24_000
MAX_TEXT_LENGTH = 4_000
MAX_TOKENS = 510
MIN_SPEED = 0.75
MAX_SPEED = 1.25
FILES = {
    "model_quantized.onnx": (
        "onnx/model_quantized.onnx", 92_361_116,
        "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478",
    ),
    f"{VOICE}.bin": (
        f"voices/{VOICE}.bin", 522_240,
        "669fe0647f9dd04fcab92f1439a40eeb4c8b4ab1f82e4996fe3d918ce4a63b73",
    ),
    "tokenizer.json": (
        "tokenizer.json", 3_497,
        "77a02c8e164413299b4b4c403b14f8e0e1c1b727db4d46a09d6327b861060a34",
    ),
}
_INITIALIZATION_LOCK = Lock()
_PHRASE_BOUNDARY = re.compile(
    r"(\n+|\s+[/|]\s+|…|[!?;]+|(?<!\d)[.,:]+|[.,:]+(?!\d))"
)
_NORMALIZE_TEXT = str.maketrans({"’": "'", "‘": "'", "–": "—", "\xa0": " "})
# Kokoro v1 uses dedicated symbols for tied English diphthongs and affricates.
# Inventory: https://github.com/hexgrad/misaki/blob/main/EN_PHONES.md
_TIED_PHONES = {
    "a^ɪ": "I", "a^ʊ": "W", "d^ʒ": "ʤ", "e^ɪ": "A", "e^ə": "ɛː",
    "t^ʃ": "ʧ", "ɔ^ɪ": "Y", "ə^ʊ": "Q", "ə^l": "ᵊl",
}


class KokoroUnavailable(RuntimeError):
    """The optional offline British reference cannot run."""


def install_model() -> None:
    """Stage each public asset by hash, reusing the pinned research cache."""
    model_dir = MODEL_DIR
    research_cache = Path(gettempdir()) / "eoi-mdd-phase5" / "Kokoro-a70f0e4"
    model_dir.mkdir(parents=True, exist_ok=True)
    for name, (remote_path, size, digest) in FILES.items():
        target = model_dir / name
        if verified(target, size, digest):
            continue
        local_copy = research_cache / name
        output = NamedTemporaryFile(prefix=".download-", dir=model_dir, delete=False)
        candidate = Path(output.name)
        try:
            with output:
                if verified(local_copy, size, digest):
                    with local_copy.open("rb") as source:
                        shutil.copyfileobj(source, output)
                else:
                    url = f"https://huggingface.co/{REPOSITORY}/resolve/{REVISION}/{remote_path}"
                    with urlopen(url, timeout=60) as response:
                        _copy_download(response, output, size, name)
            if not verified(candidate, size, digest):
                raise OSError(f"El archivo {name} no coincide con la revisión fijada.")
            candidate.replace(target)
        finally:
            candidate.unlink(missing_ok=True)
    print("Modelo Kokoro bf_emma verificado y disponible para uso sin conexion.")


def _copy_download(response, output, size: int, name: str) -> None:
    remaining = size
    while chunk := response.read(min(1024 * 1024, remaining + 1)):
        remaining -= len(chunk)
        if remaining < 0:
            raise OSError(f"La descarga de {name} supera el tamaño esperado.")
        output.write(chunk)


def _normalize_phones(phones: str) -> str:
    for source, target in _TIED_PHONES.items():
        phones = phones.replace(source, target)
    phones = re.sub(r"(\S)\u0329", r"ᵊ\1", phones)
    phones = phones.replace("ɚ", "əɹ").replace("ʲ", "j")
    return phones.translate(str.maketrans({"r": "ɹ", "ɾ": "T", "ʔ": "t", "^": "", "\u032a": ""}))


class _BritishPhonemizer:
    """One serialized British eSpeak NG dictionary for Kokoro's IPA tokens."""

    def __init__(self) -> None:
        from espeakng_loader import get_data_path, get_library_path

        data = Path(get_data_path())
        if not (data / "phontab").is_file() or not (data / "en_dict").is_file():
            raise OSError("Faltan los datos fonéticos de eSpeak NG.")
        library = ctypes.CDLL(get_library_path())
        initialize = library.espeak_Initialize
        initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        initialize.restype = ctypes.c_int
        select_voice = library.espeak_SetVoiceByName
        select_voice.argtypes = [ctypes.c_char_p]
        select_voice.restype = ctypes.c_int
        # Synchronous mode, with exit disabled if the dictionary cannot load.
        if initialize(2, 0, str(data).encode("utf-8"), 0x8000) <= 0:
            raise OSError("No se pudo cargar el diccionario de eSpeak NG.")
        if select_voice(b"English (Great Britain)") != 0:
            raise OSError("No se pudo cargar el diccionario británico.")
        self._library = library
        self._translate = library.espeak_TextToPhonemes
        self._translate.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_int, ctypes.c_int]
        self._translate.restype = ctypes.c_char_p
        self._lock = Lock()

    def _translate_phrase(self, phrase: str) -> str:
        source = ctypes.create_string_buffer(phrase.encode("utf-8"))
        cursor = ctypes.cast(source, ctypes.c_void_p)
        end = cursor.value + len(source)
        clauses = []
        while cursor.value:
            previous = cursor.value
            # UTF-8 input (1), IPA (2), and the caret as the tie mark (0x80).
            result = self._translate(ctypes.byref(cursor), 1, 0x82 | ord("^") << 8)
            if cursor.value and not previous < cursor.value < end:
                raise KokoroUnavailable("El diccionario británico no pudo leer el fragmento.")
            if result:
                clauses.append(result.decode("utf-8"))
        return _normalize_phones(" ".join(clauses)).strip()

    def __call__(self, text: str) -> str:
        pieces = _PHRASE_BOUNDARY.split(text)
        rendered = []
        with self._lock:
            for index in range(0, len(pieces), 2):
                phrase = self._translate_phrase(pieces[index].strip())
                if not phrase:
                    continue
                if index + 1 < len(pieces):
                    boundary = pieces[index + 1][0]
                    phrase += boundary if boundary in ".!?,:;…" else "."
                rendered.append(phrase)
        return " ".join(rendered)


@lru_cache(maxsize=1)
def _runtime():
    import onnxruntime as ort

    for name, (_, size, digest) in FILES.items():
        if not verified(MODEL_DIR / name, size, digest):
            raise KokoroUnavailable("Falta el modelo británico verificado. Ejecuta Instalar.cmd.")
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(MODEL_DIR / "model_quantized.onnx"),
        sess_options=options, providers=["CPUExecutionProvider"],
    )
    raw_tokenizer = (MODEL_DIR / "tokenizer.json").read_text(encoding="utf-8")
    vocab = json.loads(raw_tokenizer)["model"]["vocab"]
    styles = np.fromfile(MODEL_DIR / f"{VOICE}.bin", dtype="<f4").reshape(MAX_TOKENS, 1, 256)
    return _BritishPhonemizer(), session, vocab, styles


def synthesize_british(text: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
    """Return a 24 kHz mono practice reference in memory, without network calls."""
    text = text.translate(_NORMALIZE_TEXT).strip()
    if not text or len(text) > MAX_TEXT_LENGTH or not any(char.isalnum() for char in text):
        raise ValueError(f"Escribe hasta {MAX_TEXT_LENGTH} caracteres de texto en inglés.")
    if any(not char.isprintable() and char not in "\n\t\r" for char in text):
        raise ValueError("El texto contiene caracteres de control.")
    if not MIN_SPEED <= speed <= MAX_SPEED:
        raise ValueError(f"Elige una velocidad entre {MIN_SPEED} y {MAX_SPEED}.")
    try:
        with _INITIALIZATION_LOCK:
            phonemizer, session, vocab, styles = _runtime()
        phones = phonemizer(text)
        if not phones:
            raise ValueError("No se encontró texto pronunciable en el fragmento.")
        if set(phones) - vocab.keys():
            raise ValueError("Hay símbolos fonéticos que la voz británica no admite.")
        chunks = wrap(phones, width=MAX_TOKENS, break_long_words=False, break_on_hyphens=False)
        if max(map(len, chunks)) > MAX_TOKENS:
            raise ValueError("Divide el fragmento en palabras o frases más cortas.")
        parts = []
        for chunk in chunks:
            tokens = [vocab[symbol] for symbol in chunk]
            prediction = session.run(
                None,
                {
                    "input_ids": np.array([[0, *tokens, 0]], dtype=np.int64),
                    "style": styles[len(tokens) - 1],
                    "speed": np.asarray([speed], dtype=np.float32),
                },
            )[0]
            audio = np.asarray(prediction, dtype=np.float32).reshape(-1)
            if not len(audio) or not np.isfinite(audio).all() or not np.any(audio):
                raise KokoroUnavailable("La voz británica no generó una señal de audio utilizable.")
            if parts:
                parts.append(np.zeros(SAMPLE_RATE // 8, dtype=np.float32))
            parts.append(audio)
    except (ValueError, KokoroUnavailable):
        raise
    except Exception as error:
        raise KokoroUnavailable("La voz británica local no está disponible. Ejecuta Instalar.cmd.") from error
    return np.concatenate(parts), SAMPLE_RATE


if __name__ == "__main__":
    install_model()
