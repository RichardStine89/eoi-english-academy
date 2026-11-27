"""Exercise optional British TTS without requesting network or private audio."""

from importlib.util import find_spec
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kokoro_model import (  # noqa: E402
    FILES,
    MAX_TEXT_LENGTH,
    MODEL_DIR,
    KokoroUnavailable,
    _runtime,
    install_model,
    synthesize_british,
)


class KokoroInputTests(unittest.TestCase):
    def test_invalid_input_does_not_open_a_model(self):
        cases = [("", 1), ("?", 1), ("a" * (MAX_TEXT_LENGTH + 1), 1), ("book", 2), ("a\0b", 1)]
        with patch("kokoro_model._runtime") as runtime:
            for text, speed in cases:
                with self.subTest(length=len(text), speed=speed), self.assertRaises(ValueError):
                    synthesize_british(text, speed)
            runtime.assert_not_called()

    def test_missing_cache_provides_a_graceful_offline_error(self):
        with patch("kokoro_model.verified", return_value=False):
            _runtime.cache_clear()
            with self.assertRaisesRegex(KokoroUnavailable, "Instalar.cmd"):
                synthesize_british("Good morning.")


class KokoroProvisioningTests(unittest.TestCase):
    def test_verified_research_cache_is_copied_without_download(self):
        data = b"verified asset"
        files = {"model.onnx": ("onnx/model.onnx", len(data), sha256(data).hexdigest())}
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "eoi-mdd-phase5" / "Kokoro-a70f0e4" / "model.onnx"
            source.parent.mkdir(parents=True)
            source.write_bytes(data)
            with (
                patch("kokoro_model.MODEL_DIR", root / "destination"),
                patch("kokoro_model.FILES", files),
                patch("kokoro_model.gettempdir", return_value=temporary),
                patch("kokoro_model.urlopen", side_effect=AssertionError("La descarga era innecesaria.")),
            ):
                install_model()
            self.assertEqual(source.read_bytes(), data)
            self.assertEqual((root / "destination" / "model.onnx").read_bytes(), data)

    def test_download_must_pass_sha256_before_promotion(self):
        files = {"model.onnx": ("onnx/model.onnx", 3, sha256(b"abc").hexdigest())}
        with TemporaryDirectory() as temporary:
            destination = Path(temporary) / "destination"
            with (
                patch("kokoro_model.MODEL_DIR", destination),
                patch("kokoro_model.FILES", files),
                patch("kokoro_model.gettempdir", return_value=temporary),
                patch("kokoro_model.urlopen", return_value=BytesIO(b"xyz")),
                self.assertRaisesRegex(OSError, "revisión fijada"),
            ):
                install_model()
            self.assertEqual(list(destination.iterdir()), [])


@unittest.skipUnless(
    all((MODEL_DIR / name).is_file() for name in FILES) and find_spec("espeakng_loader"),
    "Kokoro opcional sin instalar",
)
class KokoroOfflineTests(unittest.TestCase):
    def test_british_audio_is_local_and_replayable(self):
        word = "thought"
        phrase = "Could you tell me how to get to the railway station?"
        pairs = "ship / sheep. thin / tin. full / fool. buzz / bus."
        script = "Good morning! Have you booked your train? It leaves at 10:35."
        with (
            patch("kokoro_model.urlopen", side_effect=AssertionError("La síntesis solicita red.")),
            patch("socket.socket.connect", side_effect=AssertionError("No se permiten conexiones.")),
        ):
            for source in (word, phrase, pairs, script):
                with self.subTest(source=source):
                    mono, rate = synthesize_british(source)
                    self.assertEqual(rate, 24_000)
                    self.assertEqual(mono.dtype, np.float32)
                    self.assertEqual(mono.ndim, 1)
                    self.assertGreater(len(mono), rate // 4)
                    self.assertTrue(np.isfinite(mono).all())
                    self.assertGreater(float(np.max(np.abs(mono))), 0.05)
            slow, _ = synthesize_british(phrase, 0.75)
            fast, _ = synthesize_british(phrase, 1.25)
            self.assertGreater(len(slow), len(fast))
            ship, _ = synthesize_british("ship")
            sheep, _ = synthesize_british("sheep")
            self.assertFalse(np.array_equal(ship, sheep))

    def test_british_phones_and_minimal_pairs_are_preserved(self):
        phonemize, _, _, _ = _runtime()
        for word, expected in {
            "thin": "θ", "tin": "t", "ship": "ɪ", "sheep": "iː",
            "full": "ʊ", "fool": "uː", "buzz": "z", "bus": "s", "home": "Q",
        }.items():
            with self.subTest(word=word):
                self.assertIn(expected, phonemize(word))
        self.assertNotIn("ɹ", phonemize("park"))


if __name__ == "__main__":
    unittest.main()
