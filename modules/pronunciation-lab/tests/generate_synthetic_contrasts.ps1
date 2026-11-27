param([Parameter(Mandatory)][string]$OutDir)

$ErrorActionPreference = 'Stop'
$output = [IO.Path]::GetFullPath($OutDir)
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..\..'))
$repoPrefix = $repo.TrimEnd([IO.Path]::DirectorySeparatorChar) + [IO.Path]::DirectorySeparatorChar
if ($output -eq $repo -or $output.StartsWith($repoPrefix, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Choose an output directory outside the repository.'
}
if (Test-Path -LiteralPath $output) {
    throw 'Choose a new output directory to preserve earlier runs.'
}

$voice = New-Object -ComObject SAPI.SpVoice
$selected = @($voice.GetVoices() | Where-Object { $_.GetDescription() -eq 'Microsoft Zira Desktop - English (United States)' })
if ($selected.Count -ne 1) {
    throw 'This pilot requires the pinned Microsoft Zira Desktop English voice.'
}
$voice.Voice = $selected[0]
$createWave = 3
$parseSsml = 8 -bor 256
$ipa = @{
    ah='ʌ'; ay='aɪ'; b='b'; ch='tʃ'; d='d'; dh='ð'; eh='ɛ'; er='ɚ'; f='f'; ih='ɪ'; iy='i'
    l='l'; m='m'; n='n'; ow='oʊ'; p='p'; r='ɹ'; s='s'; sh='ʃ'; t='t'; v='v'; w='w'; z='z'
}

$targets = @(
    @{ Word='then'; Phones='dh eh n'; Expected='dh'; Alternative='d' },
    @{ Word='those'; Phones='dh ow z'; Expected='dh'; Alternative='d' },
    @{ Word='thy'; Phones='dh ay'; Expected='dh'; Alternative='d' },
    @{ Word='mother'; Phones='m ah dh er'; Expected='dh'; Alternative='d' },
    @{ Word='weather'; Phones='w eh dh er'; Expected='dh'; Alternative='d' },
    @{ Word='breathe'; Phones='b r iy dh'; Expected='dh'; Alternative='d' },
    @{ Word='ship'; Phones='sh ih p'; Expected='ih'; Alternative='iy' },
    @{ Word='sit'; Phones='s ih t'; Expected='ih'; Alternative='iy' },
    @{ Word='fill'; Phones='f ih l'; Expected='ih'; Alternative='iy' },
    @{ Word='chip'; Phones='ch ih p'; Expected='ih'; Alternative='iy' },
    @{ Word='bit'; Phones='b ih t'; Expected='ih'; Alternative='iy' },
    @{ Word='live'; Phones='l ih v'; Expected='ih'; Alternative='iy' }
)

New-Item -ItemType Directory -Path $output | Out-Null
$rows = @(
    foreach ($target in $targets) {
        $tokens = @('s', 'ey') + ($target.Phones -split ' ') + @('ah', 'g', 'eh', 'n')
        $index = [Array]::IndexOf($tokens, $target.Expected)
        $prompt = "Say $($target.Word) again."
        foreach ($rate in @(0, 1)) {
            $voice.Rate = $rate
            foreach ($condition in @('expected', 'substitution')) {
                $phones = @($tokens)
                if ($condition -eq 'substitution') { $phones[$index] = $target.Alternative }
                $name = "tts-$($target.Word)-$rate-$condition"
                $file = "$name.wav"
                $path = Join-Path $output $file
                $stream = New-Object -ComObject SAPI.SpFileStream
                $stream.Open($path, $createWave, $false)
                try {
                    $voice.AudioOutputStream = $stream
                    $wordIpa = ($phones[2..($phones.Length - 5)] | ForEach-Object { $ipa[$_] }) -join ''
                    $xml = '<speak version="1.0" xml:lang="en-US">Say <phoneme alphabet="ipa" ph="' +
                        $wordIpa + '">' + $target.Word + '</phoneme> again.</speak>'
                    [void]$voice.Speak($xml, $parseSsml)
                } finally {
                    $stream.Close()
                }
                [pscustomobject]@{
                    id=$name; file=$file; word=$target.Word; prompt=$prompt; rate=$rate; condition=$condition
                    contrast=($target.Expected + '->' + $target.Alternative).ToUpperInvariant()
                    target_index=$index; phones=$phones; sha256=(Get-FileHash -LiteralPath $path).Hash.ToLowerInvariant()
                }
            }
        }
    }
)
[pscustomobject]@{ voice=$selected[0].GetDescription(); rows=$rows } |
    ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $output 'manifest.json') -Encoding utf8
Write-Output "$($rows.Count) paired phoneme-conditioned clips"
