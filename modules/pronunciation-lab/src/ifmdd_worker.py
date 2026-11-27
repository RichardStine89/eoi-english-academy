"""Replay the reviewed IF-MDD graph offline in its isolated CPU environment."""

from collections import OrderedDict
from hashlib import file_digest
import json
import math
import os
from pathlib import Path
import re
import sys

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import numpy as np
import torch
from torch.nn import functional as F
from torchaudio.models.decoder import ctc_decoder
from transformers import WavLMConfig, WavLMModel


SAMPLE_RATE = 16_000
MAX_BYTES = 30 * SAMPLE_RATE * 4
FILES = {
    "model.ckpt": "d1131b48e67758775a07edaff0d77750d037fd4bcf51615adfdf8d0d16077a2a",
    "tokenizer.ckpt": "7c18649ce9e77f51b9c68288fdfc9ab16696c4e9a47600fc1f7f441ce8ac6752",
    "perceived_ssl.ckpt": "304670a95f15f90b3787a59cc795d8b7ab6f76d72dc0770721a0f720ca9f9c18",
    "wavlm-config.json": "a3d8fe831aaf63d725b54a8ac36f3549cd4365c5086774b2c89cabbc6f9e129d",
    "wavlm-preprocessor.json": "60ca5a31e13f69ee2fbf147504c8676db5f6398fd7a6b12294341dff838edfcf",
}


@torch.inference_mode()
def decode(folder: Path, sound: np.ndarray) -> list[list]:
    for name, expected in FILES.items():
        with (folder / name).open("rb") as stream:
            if file_digest(stream, "sha256").hexdigest() != expected:
                raise ValueError(f"Checksum mismatch: {name}")

    config = WavLMConfig.from_json_file(str(folder / "wavlm-config.json"))
    config.apply_spec_augment = False
    encoder = WavLMModel(config).eval()
    checkpoint = torch.load(folder / "perceived_ssl.ckpt", map_location="cpu", weights_only=True, mmap=True)
    encoder.load_state_dict(OrderedDict((key.removeprefix("model."), value)
                                       for key, value in checkpoint.items()), strict=True)
    weights = torch.load(folder / "model.ckpt", map_location="cpu", weights_only=True)
    labels = (folder / "tokenizer.ckpt").read_text(encoding="utf-8").split("================", 1)[0]
    tags = {int(index): phone for phone, index in re.findall(r"(?m)^'([^']+)' => (\d+)$", labels)}
    if set(tags) != set(range(44)) or tags[0] != "<blank>":
        raise ValueError("Unexpected token inventory")
    decoder = ctc_decoder(lexicon=None, tokens=[tags[i] for i in range(44)], nbest=1, beam_size=50,
                          beam_threshold=50, lm_weight=2, blank_token="<blank>", sil_token="<blank>")

    waveform = torch.from_numpy(sound).unsqueeze(0)
    normalize = json.loads((folder / "wavlm-preprocessor.json").read_text(encoding="utf-8"))["do_normalize"]
    if normalize:
        waveform = F.layer_norm(waveform, waveform.shape[1:])
    frames = encoder(waveform).last_hidden_state
    for prefix in ("0.0.linear.w.", "0.0.linear_0.w."):
        frames = F.leaky_relu(F.linear(frames, weights[prefix + "weight"], weights[prefix + "bias"]))
    frames = F.layer_norm(frames, (384,), weights["0.1.weight"], weights["0.1.bias"])
    scores = F.linear(frames, weights["1.w.weight"], weights["1.w.bias"])
    probs = F.log_softmax(scores, dim=-1).contiguous()
    top = decoder(probs)[0][0]

    step = math.prod(config.conv_stride) / SAMPLE_RATE
    width = jump = 1
    for stride, kernel in zip(config.conv_stride, config.conv_kernel, strict=True):
        width += (kernel - 1) * jump
        jump *= stride
    offset = width / (2 * SAMPLE_RATE)
    tokens = []
    for token, frame in zip(top.tokens.tolist(), top.timesteps.tolist(), strict=True):
        if not token or not 0 <= frame < probs.shape[1]:
            raise ValueError("Unexpected blank or out-of-range beam frame")
        tokens.append([tags[token], round(frame * step + offset, 4)])
    return tokens


def main() -> None:
    payload = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES or len(payload) % 4:
        raise ValueError("Expected up to 30 seconds of 16 kHz mono float32 PCM")
    sound = np.frombuffer(payload, dtype="<f4").copy()
    if len(sound) < SAMPLE_RATE // 4 or not np.isfinite(sound).all() or float((sound ** 2).mean()) < 1e-8:
        print("[]")
        return
    torch.set_num_threads(6)
    torch.set_num_interop_threads(1)
    print(json.dumps(decode(Path(sys.argv[1]), sound)))


if __name__ == "__main__":
    main()
