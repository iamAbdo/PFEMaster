@echo off
echo Fixing CA index.txt file...

REM Check if CA directory exists
if not exist "CA" (
    echo Error: CA directory not found. Please run create_ca.bat first.
    pause
    exit /b 1
)

REM Backup existing index.txt if it exists
if exist "CA\index.txt" (
    echo Backing up existing index.txt...
    copy CA\index.txt CA\index.txt.backup
)

REM Create a proper empty index.txt file
echo Creating proper index.txt file...
type nul > CA\index.txt

REM Verify the file is empty
echo Verifying index.txt file...
dir CA\index.txt

echo.
echo Index.txt file has been fixed!
echo If you had an existing index.txt, it was backed up as index.txt.backup
echo.
echo You can now run create_server_cert.bat to create server certificates.
pause 