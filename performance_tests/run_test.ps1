param (
    [string]$JMeterBin = "D:\apache-jmeter-5.6.3\bin",
    [string]$TargetHost = "localhost",
    [int]$TargetPort = 8000,
    [int]$Threads = 10,
    [int]$RampUp = 5,
    [int]$Duration = 60
)

# Paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$JmxFile = "$ScriptDir\car_tracker_load_test.jmx"
$ResultsCsv = "$ScriptDir\results_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
$ReportDir = "$ScriptDir\report_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "Starting JMeter Load Test" -ForegroundColor Cyan
Write-Host "-------------------------"
Write-Host "JMeter Bin:    $JMeterBin"
Write-Host "Target:        http://${TargetHost}:${TargetPort}"
Write-Host "Threads:       $Threads"
Write-Host "Ramp Up (s):   $RampUp"
Write-Host "Duration (s):  $Duration"
Write-Host "JMX Plan:      $JmxFile"
Write-Host "-------------------------"

$JMeterExecutable = "$JMeterBin\jmeter.bat"

if (-Not (Test-Path $JMeterExecutable)) {
    Write-Error "Could not find jmeter.bat at $JMeterExecutable. Please check the path."
    exit 1
}

# Execute JMeter in non-GUI mode
$args = @(
    "-n",
    "-t", $JmxFile,
    "-l", $ResultsCsv,
    "-e", "-o", $ReportDir,
    "-Jhost=$TargetHost",
    "-Jport=$TargetPort",
    "-Jthreads=$Threads",
    "-Jrampup=$RampUp",
    "-Jduration=$Duration"
)

Write-Host "Running command: $JMeterExecutable $args"
& $JMeterExecutable $args

if ($LASTEXITCODE -eq 0) {
    Write-Host "Test completed successfully!" -ForegroundColor Green
    Write-Host "Results saved to: $ResultsCsv"
    Write-Host "HTML Report generated at: $ReportDir\index.html"
} else {
    Write-Error "Test encountered errors. Exit code: $LASTEXITCODE"
}
