@echo off
cd /d "%~dp0"
echo ============================================
echo Rally Report Generator
echo ============================================
echo.
python rally_to_email.py
echo.
echo ============================================
echo Script completed!
echo ============================================
pause