@echo off
:: Run script for ESP32 Environmental Monitoring Dashboard
:: For Windows systems

echo ========================================================
echo       ESP32 Environmental Monitoring Dashboard
echo ========================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Check if pip is installed
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip is not installed or not in your PATH.
    echo Please install pip and try again.
    pause
    exit /b 1
)

:: Check if Streamlit is installed
python -c "import streamlit" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Streamlit is not installed. Installing required packages...
    pip install -r requirements.txt
    
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to install required packages.
        echo Please try running 'pip install -r requirements.txt' manually.
        pause
        exit /b 1
    )
)

:: Check if firebase_credentials.json exists
if not exist firebase_credentials.json (
    echo Notice: firebase_credentials.json not found.
    echo The dashboard will run in demo mode with sample data.
    echo To set up Firebase authentication, run: python setup_firebase.py
    echo.
    set /p setup_firebase="Do you want to set up Firebase now? (y/n) [n]: "
    
    if /i "%setup_firebase%"=="y" (
        python setup_firebase.py
    )
)

echo.
echo Starting the dashboard...
echo Press Ctrl+C to stop the dashboard.
echo.

:: Run the dashboard
streamlit run dashboard.py

pause
