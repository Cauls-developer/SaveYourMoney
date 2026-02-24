param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath,
    [Parameter(Mandatory = $true)]
    [string]$BackendRoot
)

if (-not (Test-Path -LiteralPath $ExePath)) {
    exit 1
}

$sources = Get-ChildItem -LiteralPath $BackendRoot -Recurse -File -Include *.py, *.txt, *.yaml |
    Where-Object { $_.FullName -notmatch '\\\.venv\\|\\build\\|\\dist\\|\\__pycache__\\|\\tests\\' }

if (-not $sources) {
    exit 1
}

$latest = $sources | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$exe = Get-Item -LiteralPath $ExePath

if ($latest -and $exe.LastWriteTime -ge $latest.LastWriteTime) {
    exit 0
}

exit 1
