"""Create a local paired /DH/ to /D/ diagnostic set with the pinned Kokoro ONNX."""

import argparse
from hashlib import file_digest, sha1, sha256
import json
from pathlib import Path

import numpy as np
import onnxruntime as ort
import soundfile as sf


ARTIFACTS = {
    "model_quantized.onnx": "fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478",
    "bf_emma.bin": "669fe0647f9dd04fcab92f1439a40eeb4c8b4ab1f82e4996fe3d918ce4a63b73",
}
TOKENIZER_BLOB = "4280f55fc1c32211bc9bb4d55545759a00054ecd"
TARGETS = {
    "then": ("ðˈɛn", ("DH", "EH", "N")),
    "those": ("ðˈOz", ("DH", "OW", "Z")),
    "thy": ("ðˈI", ("DH", "AY")),
    "mother": ("mˈʌðə", ("M", "AH", "DH", "AH")),
    "weather": ("wˈɛðə", ("W", "EH", "DH", "AH")),
    "breathe": ("bɹˈiːð", ("B", "R", "IY", "DH")),
}


def render(bundle, output):
    repo = Path(__file__).resolve().parents[3]
    if output.resolve().is_relative_to(repo):
        raise ValueError("Choose private storage outside the repository")
    for name, expected in ARTIFACTS.items():
        with (bundle / name).open("rb") as source:
            if file_digest(source, "sha256").hexdigest() != expected:
                raise ValueError(f"Unexpected artifact hash: {name}")
    tokenizer = (bundle / "tokenizer.json").read_bytes()
    if sha1(f"blob {len(tokenizer)}\0".encode() + tokenizer).hexdigest() != TOKENIZER_BLOB:
        raise ValueError("Unexpected tokenizer revision")
    vocabulary = json.loads(tokenizer)["model"]["vocab"]
    styles = np.fromfile(bundle / "bf_emma.bin", dtype="<f4").reshape(510, 1, 256)
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    engine = ort.InferenceSession(str(bundle / "model_quantized.onnx"), options,
                                  providers=["CPUExecutionProvider"])
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for word, (symbols, reference) in TARGETS.items():
        index = 2 + reference.index("DH")
        for condition in ("expected", "substitution"):
            substitution = condition == "substitution"
            token_text = f"sˈA {symbols.replace('ð', 'd') if substitution else symbols} əɡˈɛn."
            tokens = [vocabulary[symbol] for symbol in token_text]
            audio = engine.run(None, {"input_ids": np.array([[0, *tokens, 0]], dtype=np.int64),
                                      "style": styles[len(tokens)-1], "speed": np.ones(1, dtype=np.float32)})[0][0]
            if not np.isfinite(audio).all() or audio.size < 6000 or np.std(audio) < .002:
                raise ValueError("Invalid generated waveform")
            name = f"kokoro-{word}-{condition}"
            path = output / f"{name}.wav"
            sf.write(path, audio, 24000, subtype="FLOAT")
            phones = ["S", "EY", *reference, "AH", "G", "EH", "N"]
            if substitution:
                phones[index] = "D"
            rows.append({"id":name,"file":path.name,"word":word,"prompt":f"Say {word} again.","rate":0,
                         "condition":condition,"contrast":"DH->D","target_index":index,"phones":phones,
                         "sha256":sha256(path.read_bytes()).hexdigest()})
    (output / "manifest.json").write_text(json.dumps({"voice":"Kokoro bf_emma","rows":rows}, indent=2)+"\n",
                                           encoding="utf-8")
    print(f"{len(rows)} paired Kokoro clips")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    render(args.bundle, args.output)
