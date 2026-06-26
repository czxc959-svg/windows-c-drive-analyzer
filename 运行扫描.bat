@echo off
chcp 65001 > nul
title C-Drive Scanner

if not exist "%~dp0reports" mkdir "%~dp0reports"

set PYTHON_EXE=
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LocalAppData%\Programs\Python\Python313\python.exe
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LocalAppData%\Programs\Python\Python312\python.exe
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set PYTHON_EXE=%LocalAppData%\Programs\Python\Python311\python.exe
if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set PYTHON_EXE=%LocalAppData%\Programs\Python\Python310\python.exe
if exist "%LocalAppData%\Programs\Python\Python39\python.exe"  set PYTHON_EXE=%LocalAppData%\Programs\Python\Python39\python.exe
if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if exist "C:\Python312\python.exe" set PYTHON_EXE=C:\Python312\python.exe
if exist "C:\Python311\python.exe" set PYTHON_EXE=C:\Python311\python.exe
if exist "%ProgramFiles%\Python313\python.exe" set PYTHON_EXE=%ProgramFiles%\Python313\python.exe
if exist "%ProgramFiles%\Python312\python.exe" set PYTHON_EXE=%ProgramFiles%\Python312\python.exe

if "%PYTHON_EXE%"=="" (
    where python > nul 2>&1
    if %errorlevel%==0 set PYTHON_EXE=python
)

if "%PYTHON_EXE%"=="" (
    echo.
    echo  [ERROR] Python not found!
    echo  Please install Python 3.9+ from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo.
echo  Python found: %PYTHON_EXE%
echo.

"%PYTHON_EXE%" "%~dp0scan.py"

if %errorlevel% neq 0 (
    echo.
    echo  [!] Script exited with error code: %errorlevel%
    echo.
)

pause