Write-Host "Starting Distributed JMeter Load Test" -ForegroundColor Cyan
Write-Host "Spinning up 1 Master and 2 Worker nodes via Docker Compose..."

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Ensure report output directory does not exist to avoid merge conflicts
$ReportPath = "$ScriptDir\report_distributed"
if (Test-Path $ReportPath) {
    Write-Host "Cleaning up old report directory..."
    Remove-Item -Recurse -Force $ReportPath
}

$CsvPath = "$ScriptDir\results_distributed.csv"
if (Test-Path $CsvPath) {
    Remove-Item -Force $CsvPath
}

Set-Location $ScriptDir

Write-Host "Running docker compose up..."
docker compose -f docker-compose.jmeter.yml up --build --abort-on-container-exit

Write-Host "Tearing down workers..."
docker compose -f docker-compose.jmeter.yml down

Write-Host "Done! Check the generated HTML report locally." -ForegroundColor Green
