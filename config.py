"""
ESP32 Environmental Monitoring System - Configuration

This file contains all configurable parameters for the environmental monitoring system.
Edit these values to match your specific setup and requirements.
"""

# WiFi Configuration
WIFI_SSID = "HomeWork"
WIFI_PASSWORD = "2916?Ajpq!"

# Device Configuration
DEVICE_ID = "esp32_env_monitor_01"
READING_INTERVAL = 60  # seconds

# Sensor Pins
DHT_PIN = 4
LDR_PIN = 36
SOIL_MOISTURE_PIN = 39

# OLED Display Configuration
DISPLAY_ENABLED = True
DISPLAY_SDA_PIN = 21
DISPLAY_SCL_PIN = 22
# EPLZON 0.96 inch OLED IIC Display Module 128x64 Pixel specifications:
# - Driver IC: SSD1306
# - Interface: I2C/IIC
# - Resolution: 128x64 pixels
# - Viewing angle: >160°
# - Operating voltage: 3.3V-5V DC
# - Power consumption: 0.04W (normal operation), 0.08W (screen illumination)
# - Default I2C address is typically 0x3C (60)
# DISPLAY_I2C_ADDR = 0x3C  # Uncomment and set if auto-detection fails

# Firebase Configuration
FIREBASE_URL = "https://microlab-data-default-rtdb.firebaseio.com/"
FIREBASE_SECRET = ""  # Leave empty when using anonymous access

# Sensor Calibration
# Adjust these values based on your specific sensors and environment
LDR_MIN = 0      # Minimum ADC value (darkest)
LDR_MAX = 4095   # Maximum ADC value (brightest)
SOIL_MIN = 0     # Minimum ADC value (driest)
SOIL_MAX = 4095  # Maximum ADC value (wettest)
