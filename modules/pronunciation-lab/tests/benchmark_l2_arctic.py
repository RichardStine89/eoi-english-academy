"""Read a fixed Spanish-L1 research slice of L2-ARCTIC without fetching full archives."""

import argparse
from collections import Counter, defaultdict
from functools import lru_cache
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[3]
REVISION = "cc02fd37197966e5de11ad737f7affd577c61992"
SOURCE = f"https://huggingface.co/datasets/chikingsley/l2-arctic-release-v5.0/resolve/{REVISION}"
SPEAKERS = {"EBVS": 283108726, "ERMS": 342407125, "MBMPS": 371611366, "NJS": 269707138}
SAMPLE_COUNT = 12
CHUNK_SIZE = 64 * 1024
PHONES = {"IH": "ɪ", "IY": "i", "UH": "ʊ", "UW": "u", "AE": "æ", "AH": "ʌ", "EH": "ɛ",
          "B": "b", "V": "v", "TH": "θ", "T": "t", "DH": "ð", "D": "d", "S": "s", "Z": "z",
          "HH": "h", "L": "l", "F": "f", "M": "m", "P": "p", "K": "k"}
TEXTGRID_INTERVAL = re.compile(r'xmin\s*=\s*([.\dEe+-]+)\s+xmax\s*=\s*([.\dEe+-]+)\s+text\s*=\s*"([^"]*)"')


class ArchiveRanges(io.RawIOBase):
    def __init__(self, speaker, size):
        self.url = f"{SOURCE}/{speaker}.zip?download=true"
        self.size = size
        self.position = 0

    def seekable(self):
        return True

    def read(self, size=-1):
        end = min(self.size, self.position + size) if size >= 0 else self.size
        chunks = []
        while self.position < end:
            block, offset = divmod(self.position, CHUNK_SIZE)
            length = min(end - self.position, CHUNK_SIZE - offset)
            chunks.append(self.block(block)[offset:offset + length])
            self.position += length
        return b"".join(chunks)

    def seek(self, offset, whence=0):
        self.position = {0: 0, 1: self.position, 2: self.size}[whence] + offset
        if self.position < 0:
            raise OSError("Invalid ZIP offset")
        return self.position

    def tell(self):
        return self.position

    @lru_cache(maxsize=48)
    def block(self, number):
        start = number * CHUNK_SIZE
        end = min(self.size, start + CHUNK_SIZE) - 1
        request = Request(f"{self.url}&range_start={start}", headers={"Range": f"bytes={start}-{end}"})
        for attempt in range(3):
            try:
                with urlopen(request, timeout=20) as response:
                    if response.status != 206 or response.headers.get("Content-Range") != f"bytes {start}-{end}/{self.size}":
                        raise OSError("The server did not return the requested archive range")
                    data = response.read(CHUNK_SIZE + 1)
                    if len(data) != end - start + 1:
                        raise OSError("Truncated range")
                    return data
            except (HTTPError, URLError, TimeoutError):
                if attempt == 2:
                    raise


def selected_members(archive):
    files = sorted(name for name in archive.namelist()
                   if re.search(r"(?i)(?:^|/)annotation/arctic_[ab]\d+\.TextGrid$", name)
                   and "/__MACOSX/" not in name)
    if len(files) < SAMPLE_COUNT:
        raise ValueError("Manual annotations not found")
    return [files[index * len(files) // SAMPLE_COUNT] for index in range(SAMPLE_COUNT)]


def download(root):
    from concurrent.futures import ThreadPoolExecutor

    def speaker_files(speaker, size):
        cache = root / speaker
        cache.mkdir(parents=True, exist_ok=True)
        if (cache / "manifest.json").exists():
            return
        with ZipFile(ArchiveRanges(speaker, size)) as archive:
            items = []
            for member in selected_members(archive):
                stem = Path(member).stem
                audio = member.rsplit("/", 2)[0] + f"/wav/{stem}.wav"
                data = {"TextGrid": archive.read(member), "wav": archive.read(audio)}
                items.append({"id": stem, "sha256": {key: sha256(value).hexdigest() for key, value in data.items()}})
                for extension, value in data.items():
                    (cache / f"{stem}.{extension}").write_bytes(value)
            (cache / "manifest.json").write_text(json.dumps(items), encoding="utf-8")

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda pair: speaker_files(*pair), SPEAKERS.items()))


def tiers(grid):
    intervals = {}
    for tier in re.split(r"(?m)^\s*item \[\d+\]:\s*$", grid)[1:]:
        name = re.search(r'name\s*=\s*"([^"]+)"', tier)
        if name:
            intervals[name[1].casefold()] = [(float(start), float(end), label.strip())
                                                 for start, end, label in TEXTGRID_INTERVAL.findall(tier)]
    return intervals


def targets(phonemes):
    for start, end, label in phonemes:
        raw = [part.strip().upper() for part in label.split(",")]
        expected = arpa_phone(raw[0])
        if len(raw) == 1 and expected is not None:
            yield start, end, expected, expected, "control"
        elif len(raw) == 3 and expected is not None and raw[-1] in {"S", "D"}:
            heard = arpa_phone(raw[1]) if raw[-1] == "S" else None
            if heard is not None or raw[-1] == "D":
                if heard != expected:
                    yield start, end, expected, heard, "substitution" if heard else "omission"


def arpa_phone(value):
    # In ARPAbet AH0 is schwa, whereas stressed AH represents STRUT.
    return "ə" if value == "AH0" else PHONES.get(re.sub(r"\d+$", "", value))


def model_phone(value):
    return value.replace("ː", "").replace("ɫ", "l").replace("l̴", "l")


def evaluate(root):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from lab import load_audio
    from acoustics import analyze
    from phonetics import analyze_phonetics

    report = Counter()
    by_contrast = defaultdict(Counter)
    experimental = Counter()
    by_experimental_contrast = defaultdict(Counter)
    for speaker in SPEAKERS:
        folder = root / speaker
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        for item in manifest:
            stem = item["id"]
            files = {ext: folder / f"{stem}.{ext}" for ext in ("TextGrid", "wav")}
            if any(sha256(path.read_bytes()).hexdigest() != item["sha256"][ext] for ext, path in files.items()):
                raise ValueError("Cache contents changed")
            grid = tiers(files["TextGrid"].read_text(encoding="utf-8-sig"))
            words = [(a, b, w) for a, b, w in grid["words"] if re.fullmatch(r"[a-zA-Z']+", w)]
            if not words:
                continue
            sound, rate = load_audio(files["wav"])
            signal = analyze(sound, rate)
            phonetics = analyze_phonetics(sound, rate, " ".join(w for _, _, w in words), signal)
            scored = phonetics["words"]
            report["takes"] += 1
            matching = [w.casefold() for _, _, w in words] == [w["expected"].casefold() for w in scored]
            for start, end, expected, heard, gold in targets(grid["phones"]):
                belongs = next((i for i, (a, b, _) in enumerate(words) if a <= (start + end) / 2 < b), None)
                if belongs is None:
                    continue
                scored_word = scored[belongs] if matching else None
                outcome = "abstain"
                if scored_word and scored_word["status"] in {"possible_deviation", "no_deviation_detected"}:
                    ref = [model_phone(p) for p in scored_word["reference_phones"]]
                    if ref.count(expected) == 1:
                        flags = [f for f in scored_word["findings"] if model_phone(f["expected"]) == expected]
                        if gold == "control":
                            outcome = "fp" if flags else "tn"
                        elif any(model_phone(f["observed"] or "") == (heard or "") for f in flags):
                            outcome = "tp"
                        else:
                            outcome = "fn"
                report[outcome] += 1
                report["positive_targets" if gold != "control" else "controls"] += 1
                if outcome == "abstain" and gold != "control":
                    report["abstain_positive"] += 1
                label = expected if gold == "control" else f"{expected}->{heard or '∅'}"
                by_contrast[label][outcome] += 1
                free = scored_word.get("free_ctc") if scored_word else None
                candidate = free.get("review_candidate") if free else None
                comparison = outcome
                if free and [model_phone(p) for p in scored_word["reference_phones"]].count(expected) == 1:
                    if candidate and candidate["expected"] == expected:
                        if gold == "control":
                            comparison = "fp"
                        elif candidate["observed"] == heard:
                            comparison = "tp"
                        elif outcome != "tp":
                            comparison = "fn"
                experimental[comparison] += 1
                if comparison == "abstain" and gold != "control":
                    experimental["abstain_positive"] += 1
                by_experimental_contrast[label][comparison] += 1
    return {"counts": report, "by_contrast": by_contrast, "counts_with_review_candidate": experimental,
            "by_contrast_with_review_candidate": by_experimental_contrast,
            "speakers": len(SPEAKERS), "revision": REVISION}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path(tempfile.gettempdir()) / "eoi-l2-arctic-research")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    cache = args.cache.resolve()
    if cache.is_relative_to(ROOT):
        parser.error("Research recordings must be cached outside Git")
    if args.download:
        download(cache)
    print(json.dumps(evaluate(cache), ensure_ascii=True, indent=2))
