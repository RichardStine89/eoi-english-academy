"""Technical checks using only generated signals and temporary storage."""

import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import av
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acoustics import analyze
from lab import (
    SAMPLE_RATE, analyze_attempt, brief_report, delete_recording, export_report,
    list_attempts, listening_evidence, load_audio, private_root, save_attempt, validate_metadata,
)
from lab_app import LabApp


METADATA = {
    "student_id": "alumno-01", "unit_id": "A1-01", "cefr": "A1",
    "activity_id": "tecnica-sintetica", "mode": "guided_reading",
    "expected_text": "Hello.", "source": "import",
}


def synthetic_signal():
    t = np.arange(3 * SAMPLE_RATE) / SAMPLE_RATE
    frequency = 170 + 25 * np.sin(2 * np.pi * 2.2 * t)
    phase = 2 * np.pi * np.cumsum(frequency) / SAMPLE_RATE
    harmonic = np.sin(phase) + 0.55 * np.sin(2 * phase) + 0.35 * np.sin(3 * phase)
    envelope = 0.12 * (0.7 + 0.3 * np.sin(2 * np.pi * 5.2 * t))
    active = ((t >= 0.20) & (t < 1.30)) | ((t >= 1.67) & (t < 2.80))
    return (harmonic * envelope * active).astype(np.float32)


def encode(path, format_name, codec):
    with av.open(str(path), "w", format=format_name) as output:
        stream = output.add_stream(codec, rate=SAMPLE_RATE)
        stream.layout = "mono"
        frame = av.AudioFrame.from_ndarray(synthetic_signal()[None, :], format="fltp", layout="mono")
        frame.sample_rate = SAMPLE_RATE
        for packet in stream.encode(frame):
            output.mux(packet)
        for packet in stream.encode(None):
            output.mux(packet)


def old_phonetic_evidence():
    return {
        "status": "analyzed", "reason": None,
        "words": [{
            "expected": "Hello", "recognized": "Etiqueta de prueba", "expected_ipa": "həˈləʊ",
            "start_seconds": 0.2, "end_seconds": 0.6, "status": "possible_deviation",
            "confidence": 0.87, "model_presence": 0.91, "observed_phones": ["x"],
            "findings": [{"kind": "substitution", "recommendation": "Corrección de prueba"}],
            "free_ctc": {"phones": [{"phone": "x"}], "review_candidate": {"kind": "substitution"}},
            "syllables": [{"start_seconds": 0.3, "end_seconds": 0.5, "model_stress_support": 0.73}],
            "aligned_phones": [{"start_seconds": 0.4, "end_seconds": 0.5, "model_support": 0.82}],
        }],
        "temporal": {"aligned_words": 1},
    }


class LabTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="eoi-lab-technical-")
        self.addCleanup(temporary.cleanup)
        self.folder = Path(temporary.name)
        self.enterContext(patch.dict(os.environ, {"LOCALAPPDATA": str(self.folder)}))

    def test_synthetic_activity_pitch_and_pauses(self):
        report = analyze_attempt(synthetic_signal(), SAMPLE_RATE, METADATA)
        observed = report["acoustics"]
        self.assertEqual(observed["status"], "measured")
        self.assertEqual(observed["metrics"]["pause_count"], 1)
        self.assertAlmostEqual(observed["metrics"]["total_pause_seconds"], 0.37, delta=0.09)
        self.assertTrue(155 <= observed["metrics"]["pitch_median_hz"] <= 185)
        self.assertIsNone(report["phonetic_findings"])
        self.assertIsNone(report["transcript"])
        self.assertFalse(report["reference"]["acoustic_comparison_performed"])

    def test_insufficient_signal_keeps_unmeasurable_metrics_null(self):
        t = np.arange(3 * SAMPLE_RATE) / SAMPLE_RATE
        examples = [np.zeros(t.size), np.ones(350) * 0.1, 0.1 * np.sin(t * 220 * 2 * np.pi),
                    np.random.default_rng(12).normal(0, 0.03, t.size), np.ones(t.size)]
        for example in examples:
            with self.subTest(size=example.size, rms=float(np.sqrt(np.mean(example**2)))):
                result = analyze(example, SAMPLE_RATE)
                self.assertEqual(result["status"], "insufficient_evidence")
                self.assertTrue(all(value is None for value in result["metrics"].values()))
                json.dumps(result, allow_nan=False)
        with self.assertRaises(ValueError):
            analyze(np.array([np.nan]), SAMPLE_RATE)

    def test_decodes_wav_mp3_and_m4a_without_modifying_inputs(self):
        for extension, container, codec in (
            ("wav", "wav", "pcm_s16le"), ("mp3", "mp3", "libmp3lame"), ("m4a", "ipod", "aac"),
        ):
            with self.subTest(extension=extension):
                path = self.folder / f"synthetic.{extension}"
                encode(path, container, codec)
                original = path.read_bytes()
                data, rate = load_audio(path)
                self.assertEqual(rate, SAMPLE_RATE)
                self.assertEqual(data.ndim, 1)
                self.assertAlmostEqual(data.size / rate, 3, delta=0.10)
                self.assertEqual(analyze(data, rate)["status"], "measured")
                self.assertEqual(path.read_bytes(), original)

    def test_invalid_audio_and_context_are_rejected(self):
        original = self.folder / "invalid.wav"
        original.write_text("This is not audio.", encoding="utf-8")
        with self.assertRaises(ValueError):
            load_audio(original)
        with self.assertRaises(ValueError):
            validate_metadata({**METADATA, "student_id": "../alumno-01"})
        with self.assertRaises(ValueError):
            validate_metadata({**METADATA, "cefr": "B1"})
        with self.assertRaises(ValueError):
            validate_metadata({**METADATA, "expected_text": ""})
        self.assertIsNone(validate_metadata({**METADATA, "mode": "spontaneous"})["expected_text"])

    def test_high_rate_windows_input_is_resampled_for_analysis(self):
        report = analyze_attempt(np.repeat(synthetic_signal(), 6), 96_000, METADATA)
        self.assertEqual(report["sample_rate_hz"], 96_000)
        self.assertEqual(report["analysis_sample_rate_hz"], SAMPLE_RATE)
        self.assertEqual(report["acoustics"]["status"], "measured")

    def test_class_report_keeps_playable_alignment_and_hides_research_predictions(self):
        original = old_phonetic_evidence()
        samples = synthetic_signal()
        with patch("lab.analyze_phonetics", return_value=original):
            report = analyze_attempt(samples, SAMPLE_RATE, METADATA)
        word, = report["phonetics"]["words"]
        self.assertEqual(word["status"], "aligned_for_listening")
        self.assertEqual(word["expected_ipa"], "həˈləʊ")
        self.assertEqual(word["aligned_phones"][0]["start_seconds"], 0.4)
        self.assertEqual(word["findings"], [])
        self.assertTrue(all(word[key] is None for key in (
            "recognized", "observed_phones", "confidence", "model_presence", "free_ctc",
        )))
        self.assertIsNone(word["syllables"][0]["model_stress_support"])
        self.assertIsNone(word["aligned_phones"][0]["model_support"])
        self.assertIsNone(report["phonetic_findings"])
        self.assertIsNone(report["confidence"]["phonetic_confidence"])
        self.assertEqual(original["words"][0]["confidence"], 0.87)
        app = SimpleNamespace(audio=(samples, SAMPLE_RATE), _word_interval=LabApp._word_interval)
        segment, rate = LabApp._word_audio(app, word)
        self.assertEqual(rate, SAMPLE_RATE)
        np.testing.assert_array_equal(segment, samples[3200:9600])
        self.assertIsNone(LabApp._word_audio(app, {**word, "alignment_supported": False}))
        self.assertIn("Tramo utilizable", LabApp._word_details(word))

    def test_archived_predictions_remain_private_and_exports_are_descriptive(self):
        signal = synthetic_signal()
        report = analyze_attempt(signal, SAMPLE_RATE, METADATA)
        save_attempt(report, signal, SAMPLE_RATE)
        report["phonetics"] = old_phonetic_evidence()
        report["phonetic_findings"] = [{"kind": "substitution", "confidence": 0.87}]
        report["confidence"]["phonetic_confidence"] = 0.87
        archived = private_root() / report["student_id"] / report["attempt_id"] / "report.json"
        archived.write_text(json.dumps(report), encoding="utf-8")
        original_bytes = archived.read_bytes()

        stored, = list_attempts(report["student_id"])
        text = brief_report(stored, stored)
        self.assertIn("comparación descriptiva", text)
        self.assertIn("1/1 palabras del guion con tramo utilizable", text)
        self.assertNotIn("Corrección de prueba", text)
        self.assertNotIn("desviación", text)
        self.assertNotIn("0.87", text)
        exported = json.loads(export_report(stored).read_text(encoding="utf-8"))
        self.assertEqual(exported["phonetics"], listening_evidence(stored["phonetics"]))
        self.assertIsNone(exported["phonetic_findings"])
        self.assertIsNone(exported["confidence"]["phonetic_confidence"])
        self.assertEqual(exported["acoustics"], stored["acoustics"])
        self.assertEqual(archived.read_bytes(), original_bytes)

    def test_separate_histories_export_idempotence_and_recording_deletion(self):
        signal = synthetic_signal()
        first = analyze_attempt(signal, SAMPLE_RATE, METADATA)
        other = analyze_attempt(signal, SAMPLE_RATE, {**METADATA, "student_id": "alumno-02"})
        second = analyze_attempt(signal, SAMPLE_RATE, METADATA)
        for report in (first, other, second, first):
            save_attempt(report, signal, SAMPLE_RATE)

        self.assertEqual(sorted(report["attempt_number"] for report in list_attempts("alumno-01")), [1, 2])
        self.assertEqual(list_attempts("alumno-02"), [other])
        self.assertIn("comparación descriptiva", brief_report(second, first))
        self.assertNotIn("comparación descriptiva", brief_report(second, other))
        self.assertNotIn(METADATA["expected_text"], brief_report(first))

        export = export_report(second)
        self.assertTrue(export.is_relative_to(private_root() / "alumno-01"))
        self.assertEqual(json.loads(export.read_text(encoding="utf-8")), second)
        self.assertFalse(delete_recording("alumno-02", first["attempt_id"]))
        self.assertTrue(delete_recording("alumno-01", first["attempt_id"]))
        self.assertFalse(delete_recording("alumno-01", first["attempt_id"]))
        self.assertEqual(len(list_attempts("alumno-01")), 2)
        self.assertEqual(list_attempts("alumno-02"), [other])
