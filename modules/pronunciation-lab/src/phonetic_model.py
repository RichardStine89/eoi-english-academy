"""Provision a pinned ZIPA release explicitly, outside the lesson workflow."""

from hashlib import file_digest
from pathlib import Path
import tempfile
from urllib.request import urlopen


MODEL = "zipa-small-crctc-500k"
REVISION = "dfe87c97662606fa6db90ad06f627d4363314744"
CACHE = Path(__file__).resolve().parents[1] / ".cache" / "pronunciada"
MODEL_DIR = CACHE / "models" / MODEL
WEIGHTS = "model.int8.onnx"
FILES = {
    WEIGHTS: (70_677_672, "d0e28b68164e8b1fbd6105100c01798828aa0855000ce9bbbd1a2cec233adf13"),
    "tokens.txt": (769, "f8e042a0c9130532b22d03ec7cae2f75a23fbec70c450c31a8efb51787b2b8fe"),
}


def verified(path: Path, size: int, sha256: str) -> bool:
    if not path.is_file() or path.stat().st_size != size:
        return False
    with path.open("rb") as file:
        return file_digest(file, "sha256").hexdigest() == sha256


def install_model() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for name, (size, digest) in FILES.items():
        target = MODEL_DIR / name
        if verified(target, size, digest):
            continue
        url = f"https://huggingface.co/anyspeech/{MODEL}/resolve/{REVISION}/{name}"
        with tempfile.TemporaryDirectory(prefix=".download-", dir=MODEL_DIR) as temporary:
            candidate = Path(temporary) / name
            with urlopen(url, timeout=60) as response, candidate.open("wb") as output:
                remaining = size
                while chunk := response.read(min(1024 * 1024, remaining + 1)):
                    remaining -= len(chunk)
                    if remaining < 0:
                        raise OSError(f"La descarga de {name} supera el tamaño esperado.")
                    output.write(chunk)
            if not verified(candidate, size, digest):
                raise OSError(f"La descarga de {name} no coincide con la revisión fijada.")
            candidate.replace(target)
    print("Modelo ZIPA int8 verificado y disponible para uso sin conexion.")


if __name__ == "__main__":
    install_model()
