# Monitor benchmark progress
$logFile = "benchmark_results\current_run.log"

Write-Host "Monitoring benchmark progress..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop monitoring (benchmark will continue running)" -ForegroundColor Yellow
Write-Host ""

$lastSize = 0
$iteration = 0

while ($true) {
    Start-Sleep -Seconds 10
    $iteration++
    
    # Check if benchmark_results directory exists
    if (Test-Path "benchmark_results") {
        $files = Get-ChildItem "benchmark_results\*.json" -ErrorAction SilentlyContinue
        if ($files) {
            $latest = $files | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            Write-Host "[$($iteration * 10)s] Latest result: $($latest.Name)" -ForegroundColor Green
        }
    }
    
    # Look for temp JSON files created by agents
    $tempJsons = Get-ChildItem "*.json" -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "^\w+_\d{4}-\d{2}-\d{2}" }
    if ($tempJsons) {
        Write-Host "[$($iteration * 10)s] Agent output files created: $($tempJsons.Count)" -ForegroundColor Yellow
    }
    
    Write-Host "[$($iteration * 10)s] Still running... (elapsed: $($iteration * 10) seconds)" -ForegroundColor Gray
}
