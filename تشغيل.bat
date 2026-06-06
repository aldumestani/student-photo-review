@echo off
chcp 65001 >nul
echo ============================================================
echo           تطبيق تنظيم صور الطلبة الخريجين
echo ============================================================
echo.
echo جاري التشغيل...
echo.
python "%~dp0app.py"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ حدث خطأ. تأكد من تثبيت Python ومكتبة openpyxl
    echo.
    pause
)
