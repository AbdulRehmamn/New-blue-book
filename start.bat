@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Blue Book Contact Scraper - Setup
echo Blue Book Contact Scraper
echo Installing required components into this folder...
echo.

if exist ".venv\Scripts\python.exe" goto dependencies
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto use_py
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto use_python

echo Python 3.10 or newer was not found. Trying Python 3.12 via Windows Package Manager...
where winget >nul 2>&1
if errorlevel 1 goto python_missing
winget install --id Python.Python.3.12 --exact --scope user --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto python_missing
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" goto use_installed
py -3.12 -m venv .venv
if errorlevel 1 goto python_missing
goto dependencies

:use_py
py -3 -m venv .venv
if errorlevel 1 goto setup_error
goto dependencies

:use_python
python -m venv .venv
if errorlevel 1 goto setup_error
goto dependencies

:use_installed
"%LocalAppData%\Programs\Python\Python312\python.exe" -m venv .venv
if errorlevel 1 goto setup_error

:dependencies
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto setup_error
".venv\Scripts\python.exe" -m playwright install chromium
if errorlevel 1 goto setup_error
".venv\Scripts\python.exe" -c "import tkinter, bs4, phonenumbers, openpyxl, playwright"
if errorlevel 1 goto setup_error
echo.
echo Setup ready. Starting the desktop app...
".venv\Scripts\python.exe" app.py
if errorlevel 1 goto app_error
exit /b 0

:python_missing
echo.
echo Python could not be installed automatically.
echo Install Python 3.12 from https://www.python.org/downloads/windows/
echo Select "Add python.exe to PATH" and include Tcl/Tk, then run start.bat again.
pause
exit /b 1

:setup_error
echo.
echo Setup failed. Check the error above and your internet connection.
echo Run start.bat again to retry. Downloaded packages are reused.
pause
exit /b 1

:app_error
echo.
echo The app stopped with an error. Keep this window open to read the error above.
pause
exit /b 1
