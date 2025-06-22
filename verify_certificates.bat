@echo off
echo Verifying ENAGEO Certificate Setup...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if pyOpenSSL is installed
python -c "import OpenSSL" >nul 2>&1
if errorlevel 1 (
    echo Error: pyOpenSSL is not installed
    echo Installing pyOpenSSL...
    pip install pyOpenSSL
    if errorlevel 1 (
        echo Failed to install pyOpenSSL
        pause
        exit /b 1
    )
)

REM Run the verification script
echo Running certificate verification...
python test_certificates.py

echo.
echo Verification complete!
pause 