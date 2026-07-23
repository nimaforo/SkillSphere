@echo off
REM Script to start Docker with data persistence
REM This keeps your database and redis data between restarts

echo.
echo ========================================
echo   SkillSphere Docker Startup Script
echo ========================================
echo.

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: docker-compose is not installed or not in PATH
    echo Please install Docker Desktop
    pause
    exit /b 1
)

echo [1/3] Starting Docker containers...
docker-compose up -d

if errorlevel 1 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo [2/3] Waiting for services to be healthy...
timeout /t 5 /nobreak

echo [3/3] Checking service status...
docker-compose ps

echo.
echo ========================================
echo   ✅ Docker started successfully!
echo ========================================
echo.
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:5174
echo.
echo Your data is SAVED between restarts!
echo.
echo To STOP containers (keep data):
echo   docker-compose stop
echo.
echo To STOP and REMOVE containers (keep data):
echo   docker-compose down
echo.
echo To COMPLETELY DELETE everything (including data):
echo   docker-compose down -v
echo.
pause
