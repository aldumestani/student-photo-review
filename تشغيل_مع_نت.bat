@echo off
title خادم مراجعة الصور + ngrok
cd /d "%~dp0"

echo.
echo ==========================================
echo   تشغيل خادم المراجعة العام + ngrok
echo ==========================================
echo.

:: Kill old processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im ngrok.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start review server
start "ReviewServer" cmd /c "python -X utf8 review_server.py & pause"

:: Wait for server
timeout /t 4 /nobreak >nul

:: Start ngrok tunnel
start "Ngrok" cmd /c "ngrok http 5050 & pause"

:: Wait and show URL
timeout /t 6 /nobreak >nul
echo.
echo ==========================================
echo   افتح الرابط العام من أي جهاز:
echo.
for /f "tokens=*" %%a in ('powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:4040/api/tunnels' -UseBasicParsing -TimeoutSec 5 | ConvertFrom-Json; $r.tunnels | ForEach-Object { $_.public_url } } catch { echo '' }"') do set NGROK_URL=%%a
if defined NGROK_URL (
    echo   %NGROK_URL%
) else (
    echo   (انتظر لحظة... افتح http://127.0.0.1:4040)
)
echo.
echo   Dashboard: http://127.0.0.1:4040
echo ==========================================
echo.
echo اضغط أي زر لإغلاق كل شيء...
pause >nul

:: Cleanup
taskkill /f /im ngrok.exe >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
