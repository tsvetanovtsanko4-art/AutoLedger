<#
.SYNOPSIS
    Runs the load test from two Docker workers. Load per worker is set through
    environment variables read by docker-compose.jmeter.yml, e.g.
        $env:DRIVERS = 100; .\run_distributed.ps1
#>
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$out = Join-Path $PSScriptRoot "results\distributed"
if (Test-Path $out) { Remove-Item -Recurse -Force $out }
New-Item -ItemType Directory -Force $out | Out-Null

try {
    docker compose -f docker-compose.jmeter.yml up --build --abort-on-container-exit --exit-code-from controller
    if ($LASTEXITCODE -ne 0) { throw "Distributed run failed (exit code $LASTEXITCODE)" }
    Write-Host "Report: $out\report\index.html" -ForegroundColor Green
}
finally {
    docker compose -f docker-compose.jmeter.yml down
}
