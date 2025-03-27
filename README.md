# ESP32 Environmental Monitoring System

This project implements an environmental monitoring system using an ESP32 microcontroller. It reads data from multiple sensors, formats it as JSON, and sends it to a Firebase Realtime Database. Optionally, it can display the readings on an OLED display.

## Features

- WiFi connectivity with configurable credentials
- Temperature and humidity monitoring using DHT11 sensor
- Light level monitoring using LDR (Light Dependent Resistor)
- Soil moisture monitoring
- JSON data formatting with device ID and timestamp
- Firebase Realtime Database integration
- Optional OLED display support
- Error handling for sensor failures and WiFi disconnections
- Data caching when WiFi is unavailable

## Hardware Requirements

- ESP32 development board
- DHT11 temperature and humidity sensor
- LDR (Light Dependent Resistor) with voltage divider circuit
- Soil moisture sensor
- Optional: SSD1306 OLED display (128x64)

## Wiring Diagram

Connect the components to the ESP32 as follows:

| Component | ESP32 Pin |
|-----------|-----------|
| DHT11 Data | GPIO 4 |
| LDR Analog Output | GPIO 36 |
| Soil Moisture Sensor Analog Output | GPIO 39 |
| OLED Display SDA (optional) | GPIO 21 |
| OLED Display SCL (optional) | GPIO 22 |

### LDR Voltage Divider Circuit

For the LDR, create a voltage divider circuit:
1. Connect one leg of the LDR to 3.3V
2. Connect the other leg to a junction with a 10kΩ resistor
3. Connect the other end of the resistor to GND
4. Connect the junction between the LDR and resistor to GPIO 36

## Software Setup

1. Install MicroPython on your ESP32 board
2. Configure the `config.py` file with your WiFi credentials and Firebase details
3. Upload both `main.py` and `config.py` to your ESP32
4. Reset the ESP32 to start the program

### Firebase Setup

1. Create a Firebase project at [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Set up a Realtime Database
3. Get your Firebase URL and authentication secret
4. Update the `config.py` file with these details

## Configuration

Edit the `config.py` file to customize the system:

```python
# WiFi Configuration
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"

# Device Configuration
DEVICE_ID = "esp32_env_monitor_01"
READING_INTERVAL = 60  # seconds

# Firebase Configuration
FIREBASE_URL = "https://your-project-id.firebaseio.com/"
FIREBASE_SECRET = "your-firebase-secret"
```

## Data Format

The system sends data to Firebase in the following JSON format:

```json
{
  "device_id": "esp32_env_monitor_01",
  "timestamp": 1616876400,
  "readings": {
    "temperature": 25,
    "humidity": 60,
    "light_level": 75.5,
    "soil_moisture": 42.3
  }
}
```

## Educational Purpose

This code is structured for educational purposes with:
- Clear function organization
- Comprehensive error handling
- Detailed comments explaining each component
- Modular design for easy understanding

## Troubleshooting

- If sensors aren't reading correctly, check your wiring and pin configurations
- For WiFi connection issues, verify your credentials in `config.py`
- If the OLED display isn't working, ensure the I2C address is correct
- For Firebase connection problems, check your URL and authentication details

## License

This project is provided for educational purposes. Feel free to modify and use it for your own projects.
# stmicrolab
# stmicrolab
