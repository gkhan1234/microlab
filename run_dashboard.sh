#!/bin/bash
# Run script for ESP32 Environmental Monitoring Dashboard
# For macOS and Linux systems

echo "========================================================"
echo "      ESP32 Environmental Monitoring Dashboard"
echo "========================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in your PATH."
    echo "Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed or not in your PATH."
    echo "Please install pip and try again."
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Streamlit is not installed. Installing required packages..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install required packages."
        echo "Please try running 'pip3 install -r requirements.txt' manually."
        exit 1
    fi
fi

# Check if firebase_credentials.json exists
if [ ! -f "firebase_credentials.json" ]; then
    echo "Notice: firebase_credentials.json not found."
    echo "The dashboard will run in demo mode with sample data."
    echo "To set up Firebase authentication, run: python3 setup_firebase.py"
    echo
    read -p "Do you want to set up Firebase now? (y/n) [n]: " setup_firebase
    setup_firebase=${setup_firebase:-n}
    
    if [[ $setup_firebase == "y" || $setup_firebase == "Y" ]]; then
        python3 setup_firebase.py
    fi
fi

echo
echo "Starting the dashboard..."
echo "Press Ctrl+C to stop the dashboard."
echo

# Run the dashboard
streamlit run dashboard.py
