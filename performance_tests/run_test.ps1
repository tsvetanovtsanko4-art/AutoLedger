<#
.SYNOPSIS
    Runs the AutoLedger JMeter plan and fails if the SLA is not met.

.EXAMPLE
    .\run_test.ps1 -Profile smoke
    .\run_test.ps1 -Profile load -TargetHost staging.example.test -TargetPort 443 -Protocol https

.NOTES
    Seed the target first so the drivers have accounts and cars:
        python -m server.seed --users 1000 --cars 3000
    JMeter is looked up in -JMeterHome, then $env:JMETER_HOME, then PATH.
#>
param (
    [ValidateSet("smoke", "load", "stress", "soak")]
    [string]$Profile = "smoke",
    [string]$TargetHost = "localhost",
    [int]$TargetPort = 8000,
    [string]$Protocol = "http",
    [string]$JMeterHome = $env:JMETER_HOME,
    # SLA: 95th percentile per request, in ms, and overall error rate in %.
    [int]$ReadP95Ms = 500,
    [int]$WriteP95Ms = 1000,
    [double]$MaxErrorPct = 1.0
)

$ErrorActionPreference = "Stop"

# visitors / drivers / sign-ups are concurrent users; times are seconds.
$profiles = @{
    smoke  = @{ visitors = 2;   drivers = 3;   signups = 1;  rampup = 10;  duration = 60 }
    load   = @{ visitors = 30;  drivers = 50;  signups = 3;  rampup = 120; duration = 900 }
    stress = @{ visitors = 100; drivers = 200; signups = 10; rampup = 600; duration = 1200 }
    soak   = @{ visitors = 20;  drivers = 40;  signups = 2;  rampup = 120; duration = 14400 }
}
$load = $profiles[$Profile]

$jmeter = if ($JMeterHome) { Join-Path $JMeterHome "bin\jmeter.bat" } else { (Get-Command jmeter -ErrorAction SilentlyContinue).Source }
if (-not $jmeter -or -not (Test-Path $jmeter)) {
    throw "JMeter not found. Pass -JMeterHome or set JMETER_HOME (e.g. D:\apache-jmeter-5.6.3)."
}

$here = $PSScriptRoot
$runDir = Join-Path $here "results\$Profile-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Force $runDir | Out-Null

$jmeterArgs = @(
    "-n", "-t", (Join-Path $here "autoledger_load_test.jmx"),
    "-l", (Join-Path $runDir "results.jtl"),
    "-j", (Join-Path $runDir "jmeter.log"),
    "-e", "-o", (Join-Path $runDir "report"),
    "-Jhost=$TargetHost", "-Jport=$TargetPort", "-Jprotocol=$Protocol",
    "-Jsla_read_ms=$ReadP95Ms", "-Jsla_write_ms=$WriteP95Ms",
    # APDEX in the HTML report: satisfied up to the read SLA, tolerated up to 4x.
    "-Jjmeter.reportgenerator.apdex_satisfied_threshold=$ReadP95Ms",
    "-Jjmeter.reportgenerator.apdex_tolerated_threshold=$($ReadP95Ms * 4)"
)
$jmeterArgs += $load.GetEnumerator() | ForEach-Object { "-J$($_.Key)=$($_.Value)" }

Write-Host "Profile $Profile against ${Protocol}://${TargetHost}:${TargetPort}: $($load.drivers) drivers, $($load.visitors) visitors, $($load.signups) sign-ups for $($load.duration)s"
& $jmeter @jmeterArgs
if ($LASTEXITCODE -ne 0) { throw "JMeter exited with code $LASTEXITCODE" }

# JMeter itself never fails a run, so compare the report against the SLA here.
$stats = Get-Content (Join-Path $runDir "report\statistics.json") -Raw | ConvertFrom-Json
$failures = @()
foreach ($row in $stats.PSObject.Properties) {
    $name = $row.Name
    $s = $row.Value
    if ($name -eq "Total") {
        if ($s.errorPct -gt $MaxErrorPct) { $failures += "error rate $([math]::Round($s.errorPct, 2))% > $MaxErrorPct%" }
        continue
    }
    $limit = if ($name -match "^(POST|PUT|PATCH)") { $WriteP95Ms } else { $ReadP95Ms }
    if ($s.pct2ResTime -gt $limit) { $failures += "$name p95 $([math]::Round($s.pct2ResTime))ms > ${limit}ms" }
}

Write-Host ""
$stats.PSObject.Properties | ForEach-Object {
    [pscustomobject]@{
        Request    = $_.Name
        Samples    = $_.Value.sampleCount
        "Error %"  = [math]::Round($_.Value.errorPct, 2)
        "p95 ms"   = [math]::Round($_.Value.pct2ResTime)
        "Req/s"    = [math]::Round($_.Value.throughput, 1)
    }
} | Format-Table -AutoSize

Write-Host "Report: $(Join-Path $runDir 'report\index.html')"
if ($failures) {
    $failures | ForEach-Object { Write-Host "SLA breach: $_" -ForegroundColor Red }
    exit 1
}
Write-Host "SLA met." -ForegroundColor Green
