# PowerShell script to start Docker with data persistence

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SkillSphere Docker Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if docker-compose is installed
try {
    docker-compose --version | Out-Null
}
catch {
    Write-Host "ERROR: docker-compose is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Starting Docker containers..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start containers" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[2/3] Waiting for services to be healthy..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "[3/3] Checking service status..." -ForegroundColor Yellow
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ Docker started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5174" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your data is SAVED between restarts!" -ForegroundColor Green
Write-Host ""
Write-Host "To STOP containers (keep data):" -ForegroundColor Yellow
Write-Host "  docker-compose stop" -ForegroundColor White
Write-Host ""
Write-Host "To STOP and REMOVE containers (keep data):" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "To COMPLETELY DELETE everything (including data):" -ForegroundColor Red
Write-Host "  docker-compose down -v" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
