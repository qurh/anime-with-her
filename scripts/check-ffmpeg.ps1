Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
  Write-Error "ffmpeg not found in PATH"
  exit 1
}

Write-Output "ffmpeg path: $($ffmpeg.Source)"
& ffmpeg -version | Select-Object -First 1
