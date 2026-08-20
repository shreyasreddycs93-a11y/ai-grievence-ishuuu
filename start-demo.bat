@echo off
setlocal
cd /d "%~dp0"

echo ===============================================
echo  CivicSahayak - starting local demo
echo ===============================================

echo.
echo [1/3] Starting Postgres (Docker container: grievance-pg)...
docker start grievance-pg >nul 2>&1
if errorlevel 1 (
    echo.
    echo Could not start the "grievance-pg" Docker container.
    echo Make sure Docker Desktop is running, then try again.
    echo.
    pause
    exit /b 1
)

echo.
echo [2/3] Building the 3 frontend apps (Landing, citizen, officer)...
pushd Landing
call npm run build
popd

pushd Frontend
call npm run build
popd

pushd OfficerFrontend
call npm run build
popd

echo.
echo [3/3] Starting the server...
echo Your browser will open automatically in a few seconds.
echo.
echo   Landing:  http://localhost:8000/
echo   Citizen:  http://localhost:8000/citizen/
echo   Officer:  http://localhost:8000/officer/
echo.
echo Close this window at any time to stop the demo.
echo ===============================================
echo.

start "" cmd /c "timeout /t 5 /nobreak >nul & start http://localhost:8000/"

cd Backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
