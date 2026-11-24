"""Local decoding, report generation and per-student storage."""

from contextlib import contextmanager
from datetime import datetime
import json
import os
from pathlib import Path
import re
import tempfile
from uuid import uuid4
import wave

import av
import numpy as np
import parselmouth

from acoustics import analyze


SAMPLE_RATE = 16_000
MAX_AUDIO_SECONDS = 180
MAX_INPUT_BYTES = 128 * 1024 * 1024
MODES = {
    "guided_reading": "Lectura guiada",
    "repetition": "Repetición",
    "minimal_pairs": "Pares mínimos",
    "spontaneous": "Speaking espontáneo",
    "tourism": "Inglés turístico",
}
_FORMATS = {".wav": "wav", ".mp3": "mp3", ".m4a": "mov"}
_STUDENT = re.compile(r"alumno-(?:0[1-9]|[1-9][0-9])")
_UNIT = re.compile(r"(A1|A2|B1|B2|C1)-(?:0[1-9]|1[0-2])")
_ACTIVITY = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}")
_ATTEMPT = re.compile(r"[0-9a-f]{32}")
_COMPARISON_FIELDS = ("student_id", "unit_id", "cefr", "activity_id", "mode", "expected_text")


def load_audio(path: str | Path) -> tuple[np.ndarray, int]:
    """Decode a user-selected file as mono floats, without modifying it."""
    source = Path(path)
    demuxer = _FORMATS.get(source.suffix.lower())
    if demuxer is None:
        raise ValueError("Elige un archivo WAV, MP3 o M4A.")
    if not source.is_file() or source.stat().st_size > MAX_INPUT_BYTES:
        raise ValueError("El archivo no existe o supera el límite de 128 MB.")

    chunks = []
    count = 0
    limit = SAMPLE_RATE * MAX_AUDIO_SECONDS
    try:
        with source.open("rb") as file, av.open(
            file, mode="r", format=demuxer,
            options={"protocol_whitelist": "file,pipe", "enable_drefs": "0"},
        ) as media:
            if not media.streams.audio:
                raise ValueError("El archivo no contiene una pista de audio.")
            resampler = av.AudioResampler(format="fltp", layout="mono", rate=SAMPLE_RATE)
            for frame in media.decode(audio=0):
                frame.pts = None
                for converted in resampler.resample(frame):
                    count += converted.samples
                    if count > limit:
                        raise ValueError("La grabación supera los 3 minutos. Importa un fragmento más corto.")
                    chunks.append(converted.to_ndarray()[0])
            for converted in resampler.resample(None):
                count += converted.samples
                if count > limit:
                    raise ValueError("La grabación supera los 3 minutos. Importa un fragmento más corto.")
                chunks.append(converted.to_ndarray()[0])
    except av.error.FFmpegError as exc:
        raise ValueError("No se pudo decodificar el audio. Comprueba el formato y el estado del archivo.") from exc

    if not chunks:
        raise ValueError("El archivo no contiene muestras de audio.")
    samples = np.concatenate(chunks).astype(np.float32, copy=False)
    if not np.isfinite(samples).all():
        raise ValueError("El archivo contiene muestras de audio inválidas.")
    return np.clip(samples, -1, 1, out=samples), SAMPLE_RATE


def validate_metadata(metadata: dict) -> dict:
    student = metadata.get("student_id", "")
    if not isinstance(student, str) or not _STUDENT.fullmatch(student):
        raise ValueError("El código del alumno debe tener el formato alumno-01.")
    unit = metadata.get("unit_id", "")
    level = _UNIT.fullmatch(unit) if isinstance(unit, str) else None
    if level is None or metadata.get("cefr") != level[1]:
        raise ValueError("Elige una unidad curricular cuyo nivel coincida con el nivel MCER.")
    activity = metadata.get("activity_id", "")
    if not isinstance(activity, str) or not _ACTIVITY.fullmatch(activity):
        raise ValueError("Usa un ID de actividad breve con letras, números, guion o guion bajo.")
    mode = metadata.get("mode")
    if not isinstance(mode, str) or mode not in MODES:
        raise ValueError("Selecciona un modo de práctica.")
    expected = metadata.get("expected_text")
    if expected is not None and (not isinstance(expected, str) or len(expected) > 4_000):
        raise ValueError("El texto de referencia debe tener como máximo 4000 caracteres.")
    expected = (expected or "").strip() or None
    if mode == "spontaneous":
        expected = None
    if mode in {"guided_reading", "repetition", "minimal_pairs"} and expected is None:
        raise ValueError("Introduce el texto que se va a leer o repetir.")
    return {
        "student_id": student, "unit_id": unit, "cefr": level[1],
        "activity_id": activity, "mode": mode, "expected_text": expected,
    }


def analyze_attempt(samples: np.ndarray, rate: int, metadata: dict) -> dict:
    context = validate_metadata(metadata)
    if isinstance(rate, bool) or not isinstance(rate, (int, np.integer)) or not 8_000 <= rate <= 192_000:
        raise ValueError("El dispositivo debe entregar audio entre 8 y 192 kHz.")
    rate = int(rate)
    analysis_rate = rate
    if rate > 48_000:
        if samples.ndim != 1 or samples.size > rate * MAX_AUDIO_SECONDS or not np.isfinite(samples).all():
            raise ValueError("El audio debe ser mono, válido y de hasta 3 minutos.")
        if samples.size:
            frame = av.AudioFrame.from_ndarray(samples.astype(np.float32, copy=False)[None, :],
                                               format="fltp", layout="mono")
            frame.sample_rate = rate
            resampler = av.AudioResampler(format="fltp", layout="mono", rate=SAMPLE_RATE)
            frames = resampler.resample(frame) + resampler.resample(None)
            samples = np.concatenate([frame.to_ndarray()[0] for frame in frames]) if frames else samples[:0]
            samples = np.clip(samples, -1, 1, out=samples)
        analysis_rate = SAMPLE_RATE
    acoustics = analyze(samples, analysis_rate)
    practice = [
        "El profesor puede elegir un objetivo de práctica tras escuchar evidencia suficiente."
    ]
    if acoustics["quality"]["status"] != "usable":
        practice.insert(0, "Si la señal dificulta la observación, repite en un lugar silencioso cerca del micrófono.")
    if context["mode"] in {"guided_reading", "repetition", "minimal_pairs"}:
        practice.append("Escucha un modelo británico autorizado y repite el mismo texto para comparar intentos.")
    return {
        "schema_version": 1,
        "attempt_id": uuid4().hex,
        "attempt_number": None,
        "created_at": datetime.now().astimezone().isoformat(timespec="milliseconds"),
        **context,
        "source": metadata.get("source") if metadata.get("source") in ("recording", "import") else None,
        "engine": {"name": "Praat / Parselmouth", "version": parselmouth.VERSION,
                   "praat_version": parselmouth.PRAAT_VERSION, "acoustic_model": None},
        "reference": {"pedagogical_model": "Inglés británico estándar contemporáneo",
                      "acoustic_comparison_performed": False},
        "sample_rate_hz": rate,
        "analysis_sample_rate_hz": analysis_rate,
        "acoustics": acoustics,
        "transcript": None,
        "phonetic_findings": None,
        "confidence": {"signal_quality": acoustics["quality"]["status"],
                       "phonetic_confidence": None},
        "not_evaluated": ["fonemas y errores por palabra", "acentuación léxica y de frase",
                          "ritmo lingüístico y entonación", "palabras por minuto y fluidez",
                          "inteligibilidad y enlace entre palabras", "acento y nota académica"],
        "practice": practice,
    }


def private_root() -> Path:
    app_data = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    directory = (app_data / "EOI English Academy" / "Pronunciation Lab").resolve()
    repository = Path(__file__).resolve().parents[3]
    if directory == repository or directory.is_relative_to(repository):
        raise OSError("La carpeta de datos del laboratorio debe quedar fuera del repositorio.")
    return directory


def _inside(directory: Path, name: str) -> Path:
    child = directory / name
    if child.resolve() != child:
        raise OSError("No se admiten accesos redirigidos dentro de la carpeta de datos.")
    return child


def _student_dir(student_id: str) -> Path:
    if not isinstance(student_id, str) or not _STUDENT.fullmatch(student_id):
        raise ValueError("Código de alumno no válido.")
    return _inside(private_root(), student_id)


def list_attempts(student_id: str, activity_id: str | None = None) -> list[dict]:
    directory = _student_dir(student_id)
    reports = []
    for entry in directory.glob("*"):
        if not _ATTEMPT.fullmatch(entry.name) or entry.resolve() != entry:
            continue
        try:
            report_file = _inside(entry, "report.json")
            if report_file.stat().st_size > 1024 * 1024:
                continue
            report = json.loads(report_file.read_text(encoding="utf-8"))
            validate_metadata(report)
            number = report.get("attempt_number")
            if (report.get("schema_version") == 1 and report["student_id"] == student_id
                and report.get("attempt_id") == entry.name and isinstance(number, int)
                and number > 0 and isinstance(report.get("created_at"), str)
                and isinstance(report.get("acoustics"), dict)
                and (activity_id is None or report["activity_id"] == activity_id)):
                reports.append(report)
        except (OSError, ValueError, AttributeError, TypeError):
            continue
    return sorted(reports, key=lambda report: (report["created_at"], report["attempt_number"]), reverse=True)


@contextmanager
def _lock_student(directory: Path):
    # The file persists so parallel launches always lock the same Windows file.
    with _inside(directory, ".write.lock").open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_EX)
            yield


def _attempt_dir(student_id: str, attempt_id: str) -> Path:
    if not isinstance(attempt_id, str) or not _ATTEMPT.fullmatch(attempt_id):
        raise ValueError("Identificador de intento no válido.")
    return _inside(_student_dir(student_id), attempt_id)


def _write_json(path: Path, report: dict) -> None:
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def save_attempt(report: dict, samples: np.ndarray, rate: int) -> None:
    context = validate_metadata(report)
    student = context["student_id"]
    target = _attempt_dir(student, report["attempt_id"])
    target.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(samples, -1, 32767 / 32768) * 32768).round().astype("<i2")
    with _lock_student(target.parent):
        related = [previous for previous in list_attempts(student, context["activity_id"])
                   if all(previous[key] == report[key] for key in ("unit_id", "mode"))]
        committed = next((previous for previous in related if previous["attempt_id"] == target.name), None)
        if committed is not None:
            report["attempt_number"] = committed["attempt_number"]
            return
        number = max((previous["attempt_number"] for previous in related), default=0) + 1
        with tempfile.TemporaryDirectory(prefix=".saving-", dir=target.parent) as temporary:
            pending = Path(temporary) / "attempt"
            pending.mkdir()
            with wave.open(str(pending / "recording.wav"), "wb") as audio:
                audio.setparams((1, 2, rate, 0, "NONE", "not compressed"))
                audio.writeframes(pcm.tobytes())
            _write_json(pending / "report.json", {**report, "attempt_number": number})
            pending.rename(target)
        report["attempt_number"] = number


def delete_recording(student_id: str, attempt_id: str) -> bool:
    path = _inside(_attempt_dir(student_id, attempt_id), "recording.wav")
    try:
        path.unlink()
    except FileNotFoundError:
        return False
    return True


def export_report(report: dict) -> Path:
    context = validate_metadata(report)
    attempt = _attempt_dir(context["student_id"], report["attempt_id"])
    directory = _inside(attempt.parent, "exports")
    directory.mkdir(parents=True, exist_ok=True)
    path = _inside(directory, f"pronunciation-attempt-{attempt.name}.json")
    with tempfile.TemporaryDirectory(prefix=".exporting-", dir=directory) as temporary:
        prepared = Path(temporary) / "report.json"
        _write_json(prepared, report)
        prepared.replace(path)
    return path


def brief_report(report: dict, previous: dict | None = None) -> str:
    acoustic = report["acoustics"]
    metrics = acoustic["metrics"]
    quality = {"usable": "utilizable", "limited": "limitada", "unusable": "no utilizable"}
    lines = [
        f"EOI Pronunciation Lab · {report['student_id']} · {report['unit_id']} · {report['activity_id']}",
        f"{MODES[report['mode']]} · intento {report['attempt_number'] or 'sin número'} · {report['created_at']}",
        f"Grabación: {acoustic['duration_seconds']:.2f} s. Señal: {quality[acoustic['quality']['status']]}.",
    ]
    if metrics.get("active_seconds") is not None:
        lines.append(f"Actividad sonora estimada: {metrics['active_seconds']:.2f} s.")
    if metrics.get("pause_count") is not None:
        lines.append(f"Pausas internas estimadas: {metrics['pause_count']} ({metrics['total_pause_seconds']:.2f} s).")
    if metrics.get("pitch_median_hz") is not None:
        lines.append(f"Frecuencia fundamental mediana: {metrics['pitch_median_hz']:.0f} Hz.")
    if acoustic["quality"].get("warnings"):
        lines.append("Señal: " + " ".join(acoustic["quality"]["warnings"]))
    if previous is not None and all(report.get(key) == previous.get(key) for key in _COMPARISON_FIELDS):
        older = previous["acoustics"]["metrics"]
        if metrics.get("active_seconds") is not None and older.get("active_seconds") is not None:
            lines.append(f"Actividad sonora en el intento {previous['attempt_number']}: "
                         f"{older['active_seconds']:.2f} s (comparación descriptiva).")
    lines.append("Pendiente de valoración humana: fonemas, acentuación, ritmo lingüístico, entonación, "
                 "fluidez, inteligibilidad y nota. El texto de referencia no se ha alineado.")
    lines.append("Práctica: " + " ".join(report["practice"]))
    return "\n".join(lines)
