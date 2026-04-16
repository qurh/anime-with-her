Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:PYTHONPATH = "apps/worker"
python -m worker.main
