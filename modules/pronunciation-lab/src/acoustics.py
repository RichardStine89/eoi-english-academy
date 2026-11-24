"""Local signal and pitch measurements for a normalized mono recording."""

import math

import numpy as np
import parselmouth


MAX_DURATION_SECONDS = 180
MIN_DURATION_SECONDS = 0.45
FRAME_SECONDS = 0.02
MIN_ACTIVITY_SECONDS = 0.22
MIN_PAUSE_SECONDS = 0.20
PITCH_STEP_SECONDS = 0.01
PITCH_FLOOR_HZ = 65.0
PITCH_CEILING_HZ = 550.0
MIN_VOICED_SECONDS = 0.20
VOICING_THRESHOLD = 0.60
CLIP_THRESHOLD = 0.999

METRIC_NAMES = (
    "active_seconds",
    "activity_fraction",
    "pause_count",
    "total_pause_seconds",
    "pauses",
    "voiced_seconds",
    "pitch_median_hz",
    "pitch_p10_hz",
    "pitch_p90_hz",
    "pitch_range_semitones",
)
LIMITATIONS = (
    "La actividad acústica y las pausas son estimaciones por energía. "
    "La actividad puede incluir ruido o sonidos ajenos al habla.",
    "El tono fundamental se estima solo en tramos periódicos utilizables. "
    "Puede haber errores de seguimiento y la variación en semitonos no evalúa la entonación.",
    "El análisis presupone una toma de una sola voz. No identifica palabras, "
    "fonemas, acento, inteligibilidad ni errores de pronunciación.",
)


def _dbfs(amplitude):
    return 20 * math.log10(amplitude) if amplitude > 0 else None


def _rounded(value, digits):
    return round(float(value), digits) if value is not None else None


def _runs(mask):
    """Return half-open frame ranges that contain True."""
    edges = np.flatnonzero(np.diff(mask, prepend=False, append=False))
    return edges.reshape(-1, 2)


def _frame_rms(samples, frame_size):
    """Measure the varying component of the signal, ignoring constant offsets."""
    complete, remainder = divmod(samples.size, frame_size)
    frames = samples[:complete * frame_size].reshape(complete, frame_size)
    rms = np.std(frames, axis=1)
    if remainder:
        rms = np.append(rms, np.std(samples[-remainder:]))
    return rms


def _activity_mask(levels, frame_seconds, threshold):
    activity = levels >= threshold
    for start, end in _runs(activity):
        if (end - start) * frame_seconds < 0.06:
            activity[start:end] = False
    for start, end in _runs(~activity):
        if start > 0 and end < activity.size and (end - start) * frame_seconds < 0.08:
            activity[start:end] = True
    return activity


def _single_carrier(samples, sample_rate, times):
    """Check for a dominant narrowband carrier in representative voiced frames."""
    window_size = round(sample_rate * 0.08)
    if samples.size < window_size:
        return False
    centers = times[np.linspace(0, times.size - 1, min(24, times.size), dtype=int)]
    starts = np.clip(
        np.rint(centers * sample_rate).astype(int) - window_size // 2,
        0,
        samples.size - window_size,
    )
    window = np.hanning(window_size)
    ratios = []
    for start in np.unique(starts):
        frame = samples[start:start + window_size]
        power = np.abs(np.fft.rfft((frame - frame.mean()) * window)) ** 2
        total = power.sum()
        if total > 0:
            peak = int(power.argmax())
            ratios.append(power[max(0, peak - 2):peak + 3].sum() / total)
    return bool(ratios and np.median(ratios) >= 0.97)


def analyze(samples: np.ndarray, sample_rate: int) -> dict:
    """Return JSON-ready observations, leaving unsupported metrics null.

    Samples must be a mono vector on the normalized digital full-scale range.
    A measurement describes the recording signal and does not certify speech.
    """
    if (
        isinstance(sample_rate, (bool, np.bool_))
        or not isinstance(sample_rate, (int, np.integer))
        or not 8000 <= sample_rate <= 48000
    ):
        raise ValueError("La frecuencia debe estar entre 8 y 48 kHz.")
    samples = np.asarray(samples)
    if samples.ndim != 1 or samples.dtype.kind not in "fiu":
        raise ValueError("El análisis requiere un vector de muestras de audio mono.")
    duration = samples.size / int(sample_rate)
    if duration > MAX_DURATION_SECONDS:
        raise ValueError("La grabación supera los 180 segundos permitidos.")
    if not np.isfinite(samples).all():
        raise ValueError("La grabación contiene muestras no finitas.")
    samples = samples.astype(np.float64, copy=False)
    peak = float(np.max(np.abs(samples))) if samples.size else 0.0
    if peak > 1.0001:
        raise ValueError("Las muestras deben estar normalizadas a escala digital completa.")
    rms = math.sqrt(float(np.dot(samples, samples)) / samples.size) if samples.size else 0.0
    clipped = (
        float(np.count_nonzero(np.abs(samples) >= CLIP_THRESHOLD) / samples.size)
        if samples.size else None
    )
    warnings = []
    quality = {
        "status": "unusable",
        "peak_dbfs": _rounded(_dbfs(peak), 2),
        "rms_dbfs": _rounded(_dbfs(rms), 2),
        "clipped_fraction": _rounded(clipped, 6),
        "signal_contrast_db": None,
        "warnings": warnings,
    }
    result = {
        "status": "insufficient_evidence",
        "duration_seconds": _rounded(duration, 3),
        "quality": quality,
        "metrics": dict.fromkeys(METRIC_NAMES),
        "limitations": list(LIMITATIONS),
    }
    if duration < MIN_DURATION_SECONDS:
        warnings.append("La toma es demasiado breve para estimar actividad y tono.")
        return result
    if clipped is not None and clipped > 0:
        warnings.append("Hay muestras cerca de escala completa; comprueba si el micrófono satura.")
        if clipped >= 0.01:
            warnings.append("Demasiadas muestras cerca del límite; reduce la ganancia y repite.")
            return result

    frame_size = round(sample_rate * FRAME_SECONDS)
    frame_seconds = frame_size / sample_rate
    rms_frames = _frame_rms(samples, frame_size)
    # A bounded upper-envelope sample also works with long pre-roll or trailing silence.
    loud = float(np.median(np.partition(rms_frames, -20)[-20:]))
    floor = float(np.percentile(rms_frames, 20))
    loud_db, floor_db = _dbfs(loud), _dbfs(floor)
    contrast = loud_db - floor_db if loud_db is not None and floor_db is not None else None
    quality["signal_contrast_db"] = _rounded(contrast, 2)
    if loud_db is None or loud_db < -58:
        warnings.append("Hay silencio o la energía útil es demasiado baja.")
        return result
    threshold_db = max(-60.0, loud_db - 28)
    if contrast is not None and contrast >= 12:
        threshold_db = max(threshold_db, floor_db + 8)
    activity_threshold = 10 ** (threshold_db / 20)
    activity = _activity_mask(rms_frames, frame_seconds, activity_threshold)
    active_ranges = _runs(activity)
    active_seconds = sum(
        min(end * frame_seconds, duration) - start * frame_seconds for start, end in active_ranges
    )
    if active_seconds < MIN_ACTIVITY_SECONDS:
        warnings.append("Hay muy poca señal continua para estimar pausas y tono.")
        return result

    try:
        pitch = parselmouth.Sound(samples, sampling_frequency=sample_rate).to_pitch_ac(
            time_step=PITCH_STEP_SECONDS,
            pitch_floor=PITCH_FLOOR_HZ,
            pitch_ceiling=PITCH_CEILING_HZ,
            voicing_threshold=VOICING_THRESHOLD,
        )
    except parselmouth.PraatError:
        warnings.append("El estimador de tono no obtuvo un seguimiento utilizable.")
        return result

    selected = pitch.selected_array
    times = pitch.xs()
    frequency = selected["frequency"]
    indexes = np.clip((times / frame_seconds).astype(int), 0, activity.size - 1)
    voiced = (
        activity[indexes]
        & (rms_frames[indexes] >= activity_threshold)
        & np.isfinite(frequency)
        & (frequency >= PITCH_FLOOR_HZ)
        & (frequency <= PITCH_CEILING_HZ)
        & (selected["strength"] >= VOICING_THRESHOLD)
    )
    voiced_seconds = np.count_nonzero(voiced) * PITCH_STEP_SECONDS
    if voiced_seconds < max(MIN_VOICED_SECONDS, 0.18 * active_seconds):
        warnings.append("La señal puede contener ruido o muy poca periodicidad vocal utilizable.")
        return result

    low, median, high = np.percentile(frequency[voiced], [10, 50, 90])
    semitones = 12 * math.log2(high / low)
    quiet_level, loud_level = np.percentile(rms_frames[indexes[voiced]], [10, 90])
    level_range = _dbfs(loud_level) - _dbfs(quiet_level)
    if _single_carrier(samples, sample_rate, times[voiced]) or (semitones < 0.65 and level_range < 4):
        warnings.append("La señal es demasiado tonal o estacionaria para estimar actividad vocal.")
        return result

    if contrast is not None and contrast < 10:
        warnings.append("Hay poco contraste entre niveles; las pausas podrían ser imprecisas.")
    pauses = []
    for (_, start), (end, _) in zip(active_ranges[:-1], active_ranges[1:]):
        pause_duration = (end - start) * frame_seconds
        if pause_duration >= MIN_PAUSE_SECONDS:
            pauses.append({
                "start_seconds": _rounded(start * frame_seconds, 3),
                "end_seconds": _rounded(end * frame_seconds, 3),
                "duration_seconds": _rounded(pause_duration, 3),
            })
    quality["status"] = "limited" if warnings else "usable"
    result["status"] = "measured"
    result["metrics"] = {
        "active_seconds": _rounded(active_seconds, 3),
        "activity_fraction": _rounded(active_seconds / duration, 4),
        "pause_count": len(pauses),
        "total_pause_seconds": _rounded(sum(pause["duration_seconds"] for pause in pauses), 3),
        "pauses": pauses,
        "voiced_seconds": _rounded(min(voiced_seconds, active_seconds), 3),
        "pitch_median_hz": _rounded(median, 1),
        "pitch_p10_hz": _rounded(low, 1),
        "pitch_p90_hz": _rounded(high, 1),
        "pitch_range_semitones": _rounded(semitones, 2),
    }
    return result
