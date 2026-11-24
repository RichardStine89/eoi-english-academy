param([string]$Python = (Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'))

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$synthesizer = [System.Speech.Synthesis.SpeechSynthesizer]::new()
$folder = Join-Path ([IO.Path]::GetTempPath()) ('eoi-lab-sapi-' + [guid]::NewGuid().ToString('N'))
$null = [IO.Directory]::CreateDirectory($folder)
$env:EOI_LAB_SMOKE_FOLDER = $folder
$env:EOI_LAB_SMOKE_SOURCE = (Resolve-Path (Join-Path $PSScriptRoot '..\src')).Path
$pairs = @('ship sheep', 'live leave', 'full fool', 'three tree', 'very berry', 'hat hut', 'bad bed')

try {
    $voices = @($synthesizer.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Culture.Name -like 'en-*' } | Select-Object -First 2)
    if (-not $voices.Count) { throw 'Se necesita al menos una voz SAPI de ingles para esta prueba sintetica.' }
    for ($index = 0; $index -lt $voices.Count; $index++) {
        $synthesizer.SelectVoice($voices[$index].VoiceInfo.Name)
        foreach ($word in ($pairs -split ' ')) {
            $speech = if ($word -in @('live', 'leave')) { "I $word here." } else { "I said $word again." }
            $synthesizer.SetOutputToWaveFile((Join-Path $folder "$index-$word.wav"))
            $synthesizer.Speak($speech)
            $synthesizer.SetOutputToNull()
        }
    }
    @'
from collections import Counter
import json
import os
from pathlib import Path
import sys
import time
import urllib.request

sys.path.insert(0, os.environ["EOI_LAB_SMOKE_SOURCE"])
from acoustics import analyze
from lab import load_audio
from phonetics import _scorer, analyze_phonetics


def block_network(*args, **kwargs):
    raise AssertionError("Inference attempted a network transfer")


urllib.request.urlopen = block_network
started = time.perf_counter()
_scorer()
cold = round((time.perf_counter() - started) * 1000)
pairs = [("ship", "sheep"), ("live", "leave"), ("full", "fool"), ("three", "tree"),
         ("very", "berry"), ("hat", "hut"), ("bad", "bed")]
other = {word: alternate for pair in pairs for word, alternate in (pair, pair[::-1])}
results, timings = [], []
for path in sorted(Path(os.environ["EOI_LAB_SMOKE_FOLDER"]).glob("*.wav")):
    voice, spoken = path.stem.split("-", 1)
    wav, rate = load_audio(path)
    signal = analyze(wav, rate)
    for expected in (spoken, other[spoken]):
        prompt = f"I {expected} here." if expected in {"live", "leave"} else f"I said {expected} again."
        started = time.perf_counter()
        result = analyze_phonetics(wav, rate, prompt, signal)
        timings.append(round((time.perf_counter() - started) * 1000))
        row = next((word for word in result["words"] if word["expected"].casefold() == expected), None)
        results.append({"voice": voice, "spoken": spoken, "expected": expected,
                        "status": row["status"] if row else result["status"],
                        "findings": [(x["expected"], x["observed"]) for x in row["findings"]] if row else []})
assert any(row["status"] == "no_deviation_detected" for row in results if row["spoken"] == row["expected"])
assert any(row["findings"] for row in results if row["spoken"] != row["expected"])
assert all(row["status"] != "not_evaluated" for row in results)
print(json.dumps({"sapi_voices": len({x["voice"] for x in results}), "tests": len(results), "cold_ms": cold,
                  "warm_med_ms": sorted(timings)[len(timings) // 2],
                  "matching": Counter(x["status"] for x in results if x["spoken"] == x["expected"]),
                  "different_word": Counter(x["status"] for x in results if x["spoken"] != x["expected"]),
                  "findings": [x for x in results if x["findings"]]}, ensure_ascii=True))
'@ | & $Python -
    if ($LASTEXITCODE -ne 0) { throw 'La prueba fonetica sintetica fallo.' }
} finally {
    $synthesizer.Dispose()
    Get-ChildItem -LiteralPath $folder -File -Filter '*.wav' | Remove-Item
    [IO.Directory]::Delete($folder)
}
