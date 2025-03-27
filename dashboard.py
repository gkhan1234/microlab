"""
ESP32 Environmental Monitoring Dashboard

This Streamlit application visualizes environmental monitoring data from a Firebase Realtime Database.
It provides real-time data display, time-series charts, statistical analysis, and data export functionality.

Features:
- Authentication and connection to Firebase Realtime Database
- Device selector to choose which environmental monitor to display
- Time range selector (Last Hour, Last Day, Last Week, Last Month)
- Real-time data display showing current readings
- Time-series charts for each environmental parameter
- Statistical analysis showing min, max, average, and trends
- Data export functionality to download readings as CSV
- Sample data generator for testing when no real data is available

Author: Generated by Cline
Date: March 25, 2025
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import firebase_admin
from firebase_admin import credentials, db
import datetime
import time
import json
import os
import base64
from io import StringIO
import pytz
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="Environmental Monitoring Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for responsive design
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stPlotlyChart {
        width: 100%;
    }
    .css-1d391kg {
        padding: 1rem 1rem 1rem 1rem;
    }
    @media (max-width: 768px) {
        .reportview-container .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    }
    .info-box {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .value-box {
        background-color: #ffffff;
        border-radius: 5px;
        padding: 15px;
        margin: 5px;
        text-align: center;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
    }
    .value-title {
        font-size: 14px;
        color: #555;
    }
    .value-content {
        font-size: 24px;
        font-weight: bold;
        margin: 10px 0;
    }
    .value-unit {
        font-size: 12px;
        color: #888;
    }
    .value-trend {
        font-size: 12px;
    }
    .trend-up {
        color: #f63366;
    }
    .trend-down {
        color: #0068c9;
    }
    .trend-neutral {
        color: #888888;
    }
</style>
""", unsafe_allow_html=True)

#===============================================================================
# FIREBASE CONNECTION
#===============================================================================

@st.cache_resource
def initialize_firebase():
    """Initialize Firebase connection with error handling."""
    try:
        # Check if the app is already initialized
        if not firebase_admin._apps:
            # Path to your Firebase credentials file
            # For deployment, use st.secrets for sensitive information
            if 'FIREBASE_CREDENTIALS' in st.secrets:
                # Use secrets for deployed app
                cred_dict = json.loads(st.secrets["FIREBASE_CREDENTIALS"])
                cred = credentials.Certificate(cred_dict)
                firebase_url = st.secrets["FIREBASE_URL"]
            else:
                # Local development - look for credentials file
                cred_path = "firebase_credentials.json"
                if os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    # Read URL from the same file
                    with open(cred_path, 'r') as f:
                        config = json.load(f)
                        firebase_url = config.get("databaseURL", "https://microlab-data-default-rtdb.firebaseio.com/")
                else:
                    # Use anonymous authentication for demo purposes
                    firebase_url = "https://microlab-data-default-rtdb.firebaseio.com/"
                    return None, firebase_url, "demo"
            
            # Initialize the app
            firebase_admin.initialize_app(cred, {
                'databaseURL': firebase_url
            })
            
        # Get a database reference
        ref = db.reference('/')
        return ref, firebase_url, "connected"
    except Exception as e:
        st.error(f"Failed to connect to Firebase: {e}")
        return None, "https://microlab-data-default-rtdb.firebaseio.com/", "error"

#===============================================================================
# DATA FUNCTIONS
#===============================================================================

def get_devices(ref):
    """Get list of available devices from Firebase."""
    if ref is None or st.session_state.connection_status == "demo":
        # Return sample devices for demo mode
        return ["esp32_env_monitor_01", "esp32_env_monitor_02", "classroom_monitor"]
    
    try:
        # Get readings node which contains device data
        readings_ref = ref.child('readings')
        devices = readings_ref.get()
        if devices:
            return list(devices.keys())
        return []
    except Exception as e:
        st.error(f"Error fetching devices: {e}")
        return []

def get_time_range_timestamps(time_range):
    """Convert time range selection to start and end timestamps."""
    now = datetime.now()
    
    if time_range == "Last Hour":
        start_time = now - timedelta(hours=1)
    elif time_range == "Last Day":
        start_time = now - timedelta(days=1)
    elif time_range == "Last Week":
        start_time = now - timedelta(weeks=1)
    elif time_range == "Last Month":
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(hours=1)  # Default to last hour
    
    # Convert to Unix timestamps
    end_timestamp = time.mktime(now.timetuple())
    start_timestamp = time.mktime(start_time.timetuple())
    
    return start_timestamp, end_timestamp

def get_device_data(ref, device_id, start_timestamp, end_timestamp):
    """Get device data from Firebase within the specified time range."""
    if ref is None or st.session_state.connection_status == "demo":
        # Generate sample data for demo mode
        return generate_sample_data(device_id, start_timestamp, end_timestamp)
    
    try:
        # Get readings for the selected device
        device_ref = ref.child(f'readings/{device_id}')
        all_readings = device_ref.get()
        
        if not all_readings:
            return pd.DataFrame()
        
        # Convert to DataFrame and filter by timestamp
        data_list = []
        for timestamp, reading in all_readings.items():
            # Skip entries without timestamp or readings
            if 'timestamp' not in reading or 'readings' not in reading:
                continue
                
            reading_timestamp = reading['timestamp']
            
            # Check if timestamp is within range
            if start_timestamp <= reading_timestamp <= end_timestamp:
                # Extract readings
                readings = reading['readings']
                
                # Create a row with all data
                row = {
                    'timestamp': reading_timestamp,
                    'datetime': datetime.fromtimestamp(reading_timestamp),
                    'temperature': readings.get('temperature'),
                    'humidity': readings.get('humidity'),
                    'light_level': readings.get('light_level'),
                    'soil_moisture': readings.get('soil_moisture')
                }
                data_list.append(row)
        
        # Create DataFrame
        if data_list:
            df = pd.DataFrame(data_list)
            df = df.sort_values('timestamp')
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def generate_sample_data(device_id, start_timestamp, end_timestamp):
    """Generate sample data for demo purposes."""
    # Calculate number of data points (one reading every 5 minutes)
    duration = end_timestamp - start_timestamp
    num_points = int(duration / 300) + 1  # 300 seconds = 5 minutes
    
    # Create timestamp range
    timestamps = np.linspace(start_timestamp, end_timestamp, num_points)
    
    # Generate sample data with realistic patterns
    hours = [(datetime.fromtimestamp(ts).hour + datetime.fromtimestamp(ts).minute/60) for ts in timestamps]
    days = [(datetime.fromtimestamp(ts).weekday()) for ts in timestamps]
    
    # Temperature: daily cycle + random noise
    temp_base = 22 + 5 * np.sin(np.array(hours) * np.pi / 12)  # Daily cycle
    temperature = temp_base + np.random.normal(0, 1, num_points)  # Add noise
    
    # Humidity: inverse to temperature + random noise
    humidity_base = 60 - 15 * np.sin(np.array(hours) * np.pi / 12)  # Inverse to temperature
    humidity = humidity_base + np.random.normal(0, 5, num_points)
    humidity = np.clip(humidity, 0, 100)  # Clip to valid range
    
    # Light level: daytime pattern
    light_base = np.zeros(num_points)
    for i, hour in enumerate(hours):
        if 6 <= hour < 18:  # Daytime
            # Peak at noon
            light_base[i] = 90 * np.sin(np.pi * (hour - 6) / 12)
        else:  # Nighttime
            light_base[i] = 0
    light_level = light_base + np.random.normal(0, 5, num_points)
    light_level = np.clip(light_level, 0, 100)  # Clip to valid range
    
    # Soil moisture: decreasing over time with occasional watering
    moisture_base = np.linspace(80, 30, num_points)  # Gradually decreasing
    
    # Add "watering events"
    watering_days = [2, 5]  # Water on Tuesday and Friday
    for i, day in enumerate(days):
        if day in watering_days and hours[i] > 8 and hours[i] < 10:
            # Reset moisture after watering
            moisture_base[i:] = 80
    
    soil_moisture = moisture_base + np.random.normal(0, 3, num_points)
    soil_moisture = np.clip(soil_moisture, 0, 100)  # Clip to valid range
    
    # Create DataFrame
    data = {
        'timestamp': timestamps,
        'datetime': [datetime.fromtimestamp(ts) for ts in timestamps],
        'temperature': temperature,
        'humidity': humidity,
        'light_level': light_level,
        'soil_moisture': soil_moisture
    }
    
    return pd.DataFrame(data)

def get_download_link(df):
    """Generate a download link for the data as CSV."""
    if df.empty:
        return ""
    
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="environmental_data.csv">Download CSV File</a>'
    return href

def calculate_statistics(df):
    """Calculate statistics for each environmental parameter."""
    if df.empty:
        return {
            'temperature': {'min': None, 'max': None, 'avg': None, 'trend': 0},
            'humidity': {'min': None, 'max': None, 'avg': None, 'trend': 0},
            'light_level': {'min': None, 'max': None, 'avg': None, 'trend': 0},
            'soil_moisture': {'min': None, 'max': None, 'avg': None, 'trend': 0}
        }
    
    stats = {}
    for param in ['temperature', 'humidity', 'light_level', 'soil_moisture']:
        if param in df.columns:
            # Filter out None values
            param_data = df[param].dropna()
            
            if len(param_data) > 0:
                # Calculate basic statistics
                min_val = param_data.min()
                max_val = param_data.max()
                avg_val = param_data.mean()
                
                # Calculate trend (positive or negative)
                if len(param_data) >= 2:
                    # Use simple linear regression for trend
                    x = np.arange(len(param_data))
                    y = param_data.values
                    
                    # Calculate slope using least squares
                    slope = np.polyfit(x, y, 1)[0]
                    
                    # Normalize trend to be between -1 and 1
                    trend = np.tanh(slope * 10)  # Scale and bound the trend
                else:
                    trend = 0
                
                stats[param] = {
                    'min': min_val,
                    'max': max_val,
                    'avg': avg_val,
                    'trend': trend
                }
            else:
                stats[param] = {'min': None, 'max': None, 'avg': None, 'trend': 0}
        else:
            stats[param] = {'min': None, 'max': None, 'avg': None, 'trend': 0}
    
    return stats

#===============================================================================
# UI COMPONENTS
#===============================================================================

def render_header():
    """Render the dashboard header."""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/1902/1902203.png", width=100)
    
    with col2:
        st.title("Environmental Monitoring Dashboard")
        st.markdown("""
        This dashboard visualizes data from ESP32-based environmental monitoring systems.
        Select a device and time range to view real-time data, trends, and statistics.
        """)

def render_sidebar(ref):
    """Render the sidebar with controls."""
    st.sidebar.header("Dashboard Controls")
    
    # Connection status indicator
    if st.session_state.connection_status == "connected":
        st.sidebar.success("✅ Connected to Firebase")
    elif st.session_state.connection_status == "error":
        st.sidebar.error("❌ Firebase Connection Error")
        st.sidebar.info("Using sample data for demonstration")
    else:  # Demo mode
        st.sidebar.info("ℹ️ Demo Mode: Using sample data")
    
    # Device selector
    devices = get_devices(ref)
    if not devices:
        st.sidebar.warning("No devices found")
        selected_device = None
    else:
        selected_device = st.sidebar.selectbox(
            "Select Device",
            devices,
            index=0,
            help="Choose which environmental monitor to display"
        )
    
    # Time range selector
    time_range = st.sidebar.radio(
        "Select Time Range",
        ["Last Hour", "Last Day", "Last Week", "Last Month"],
        index=1,  # Default to Last Day
        help="Choose the time period for data visualization"
    )
    
    # Data refresh button
    refresh = st.sidebar.button("Refresh Data")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox(
        "Auto-refresh (30s)",
        value=False,
        help="Automatically refresh data every 30 seconds"
    )
    
    # Educational information
    st.sidebar.markdown("---")
    st.sidebar.subheader("About This Dashboard")
    st.sidebar.markdown("""
    This dashboard visualizes environmental data collected by ESP32 microcontrollers with various sensors:
    
    - **Temperature**: Measured in °C using DHT11 sensor
    - **Humidity**: Measured in % using DHT11 sensor
    - **Light Level**: Measured in % using LDR sensor
    - **Soil Moisture**: Measured in % using soil moisture sensor
    
    The data is stored in a Firebase Realtime Database and updated regularly.
    """)
    
    # Credits
    st.sidebar.markdown("---")
    st.sidebar.markdown("Created for educational purposes | 2025")
    
    return selected_device, time_range, refresh, auto_refresh

def render_current_readings(df, device_id):
    """Render the current readings section."""
    st.subheader("Current Readings")
    
    if df.empty:
        st.info("No data available for the selected time range")
        return
    
    # Get the most recent reading
    latest = df.iloc[-1]
    
    # Create columns for each reading
    col1, col2, col3, col4 = st.columns(4)
    
    # Temperature
    with col1:
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Temperature</div>
                <div class="value-content">{latest['temperature']:.1f}</div>
                <div class="value-unit">°C</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Humidity
    with col2:
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Humidity</div>
                <div class="value-content">{latest['humidity']:.1f}</div>
                <div class="value-unit">%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Light Level
    with col3:
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Light Level</div>
                <div class="value-content">{latest['light_level']:.1f}</div>
                <div class="value-unit">%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Soil Moisture
    with col4:
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Soil Moisture</div>
                <div class="value-content">{latest['soil_moisture']:.1f}</div>
                <div class="value-unit">%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Last updated time
    st.markdown(f"Last updated: {latest['datetime'].strftime('%Y-%m-%d %H:%M:%S')}")

def render_time_series_charts(df, time_range):
    """Render time series charts for each parameter."""
    st.subheader("Time Series Data")
    
    if df.empty:
        st.info("No data available for the selected time range")
        return
    
    # Create tabs for different visualization options
    tab1, tab2 = st.tabs(["Individual Charts", "Combined Chart"])
    
    with tab1:
        # Temperature chart
        fig_temp = px.line(
            df,
            x='datetime',
            y='temperature',
            title='Temperature Over Time',
            labels={'temperature': 'Temperature (°C)', 'datetime': 'Time'},
            line_shape='spline',
            color_discrete_sequence=['#FF5733']
        )
        fig_temp.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Humidity chart
        fig_humid = px.line(
            df,
            x='datetime',
            y='humidity',
            title='Humidity Over Time',
            labels={'humidity': 'Humidity (%)', 'datetime': 'Time'},
            line_shape='spline',
            color_discrete_sequence=['#33A1FF']
        )
        fig_humid.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_humid, use_container_width=True)
        
        # Light level chart
        fig_light = px.line(
            df,
            x='datetime',
            y='light_level',
            title='Light Level Over Time',
            labels={'light_level': 'Light Level (%)', 'datetime': 'Time'},
            line_shape='spline',
            color_discrete_sequence=['#FFC300']
        )
        fig_light.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_light, use_container_width=True)
        
        # Soil moisture chart
        fig_soil = px.line(
            df,
            x='datetime',
            y='soil_moisture',
            title='Soil Moisture Over Time',
            labels={'soil_moisture': 'Soil Moisture (%)', 'datetime': 'Time'},
            line_shape='spline',
            color_discrete_sequence=['#8B4513']
        )
        fig_soil.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_soil, use_container_width=True)
    
    with tab2:
        # Create a combined chart with all parameters
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add temperature trace
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['temperature'],
                name="Temperature (°C)",
                line=dict(color='#FF5733', width=2),
                mode='lines'
            ),
            secondary_y=False,
        )
        
        # Add humidity trace
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['humidity'],
                name="Humidity (%)",
                line=dict(color='#33A1FF', width=2),
                mode='lines'
            ),
            secondary_y=False,
        )
        
        # Add light level trace
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['light_level'],
                name="Light Level (%)",
                line=dict(color='#FFC300', width=2),
                mode='lines'
            ),
            secondary_y=True,
        )
        
        # Add soil moisture trace
        fig.add_trace(
            go.Scatter(
                x=df['datetime'],
                y=df['soil_moisture'],
                name="Soil Moisture (%)",
                line=dict(color='#8B4513', width=2),
                mode='lines'
            ),
            secondary_y=True,
        )
        
        # Set titles
        fig.update_layout(
            title_text="Combined Environmental Data",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Temperature (°C) / Humidity (%)", secondary_y=False)
        fig.update_yaxes(title_text="Light Level (%) / Soil Moisture (%)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.markdown("""
        <div class="info-box">
        <strong>Understanding the Combined Chart:</strong><br>
        This chart shows all environmental parameters together to help visualize relationships:
        <ul>
            <li>Left Y-axis: Temperature (red) and Humidity (blue)</li>
            <li>Right Y-axis: Light Level (yellow) and Soil Moisture (brown)</li>
        </ul>
        Look for patterns such as:
        <ul>
            <li>Inverse relationship between temperature and humidity</li>
            <li>Correlation between light levels and temperature</li>
            <li>Soil moisture decreasing over time until watering events</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def render_statistics(df):
    """Render statistical analysis section."""
    st.subheader("Statistical Analysis")
    
    if df.empty:
        st.info("No data available for the selected time range")
        return
    
    # Calculate statistics
    stats = calculate_statistics(df)
    
    # Create columns for each parameter
    col1, col2, col3, col4 = st.columns(4)
    
    # Temperature statistics
    with col1:
        temp_stats = stats['temperature']
        trend_icon = "↑" if temp_stats['trend'] > 0.1 else ("↓" if temp_stats['trend'] < -0.1 else "→")
        trend_class = "trend-up" if temp_stats['trend'] > 0.1 else ("trend-down" if temp_stats['trend'] < -0.1 else "trend-neutral")
        
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Temperature Statistics</div>
                <div>Min: {temp_stats['min']:.1f} °C</div>
                <div>Max: {temp_stats['max']:.1f} °C</div>
                <div>Avg: {temp_stats['avg']:.1f} °C</div>
                <div class="value-trend {trend_class}">Trend: {trend_icon}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Humidity statistics
    with col2:
        humid_stats = stats['humidity']
        trend_icon = "↑" if humid_stats['trend'] > 0.1 else ("↓" if humid_stats['trend'] < -0.1 else "→")
        trend_class = "trend-up" if humid_stats['trend'] > 0.1 else ("trend-down" if humid_stats['trend'] < -0.1 else "trend-neutral")
        
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Humidity Statistics</div>
                <div>Min: {humid_stats['min']:.1f} %</div>
                <div>Max: {humid_stats['max']:.1f} %</div>
                <div>Avg: {humid_stats['avg']:.1f} %</div>
                <div class="value-trend {trend_class}">Trend: {trend_icon}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Light level statistics
    with col3:
        light_stats = stats['light_level']
        trend_icon = "↑" if light_stats['trend'] > 0.1 else ("↓" if light_stats['trend'] < -0.1 else "→")
        trend_class = "trend-up" if light_stats['trend'] > 0.1 else ("trend-down" if light_stats['trend'] < -0.1 else "trend-neutral")
        
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Light Level Statistics</div>
                <div>Min: {light_stats['min']:.1f} %</div>
                <div>Max: {light_stats['max']:.1f} %</div>
                <div>Avg: {light_stats['avg']:.1f} %</div>
                <div class="value-trend {trend_class}">Trend: {trend_icon}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Soil moisture statistics
    with col4:
        soil_stats = stats['soil_moisture']
        trend_icon = "↑" if soil_stats['trend'] > 0.1 else ("↓" if soil_stats['trend'] < -0.1 else "→")
        trend_class = "trend-up" if soil_stats['trend'] > 0.1 else ("trend-down" if soil_stats['trend'] < -0.1 else "trend-neutral")
        
        st.markdown(
            f"""
            <div class="value-box">
                <div class="value-title">Soil Moisture Statistics</div>
                <div>Min: {soil_stats['min']:.1f} %</div>
                <div>Max: {soil_stats['max']:.1f} %</div>
                <div>Avg: {soil_stats['avg']:.1f} %</div>
                <div class="value-trend {trend_class}">Trend: {trend_icon}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Add interpretation guidance
    st.markdown("""
    <div class="info-box">
    <strong>Interpreting the Statistics:</strong><br>
    <ul>
        <li><strong>Temperature:</strong> Optimal range for most plants is 20-25°C. Extreme values can stress plants.</li>
        <li><strong>Humidity:</strong> Most plants prefer 40-60% humidity. Too low can cause wilting, too high can promote fungal growth.</li>
        <li><strong>Light Level:</strong> Different plants have different light requirements. Monitor patterns to ensure adequate light.</li>
        <li><strong>Soil Moisture:</strong> Aim for 40-60% for most plants. Below 30% indicates watering is needed.</li>
    </ul>
    <strong>Trend Indicators:</strong> ↑ Rising | ↓ Falling | → Stable
    </div>
    """, unsafe_allow_html=True)

def render_data_export(df):
    """Render data export section."""
    st.subheader("Data Export")
    
    if df.empty:
        st.info("No data available to export")
        return
    
    # Create download link
    st.markdown(get_download_link(df), unsafe_allow_html=True)
    
    # Show data preview
    with st.expander("Preview Data"):
        st.dataframe(df)

#===============================================================================
# MAIN APPLICATION
#===============================================================================

def main():
    """Main application function."""
    # Initialize session state for auto-refresh
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = time.time()
    
    if 'connection_status' not in st.session_state:
        st.session_state.connection_status = "unknown"
    
    # Initialize Firebase
    ref, firebase_url, connection_status = initialize_firebase()
    st.session_state.connection_status = connection_status
    
    # Render header
    render_header()
    
    # Render sidebar and get user selections
    selected_device, time_range, refresh, auto_refresh = render_sidebar(ref)
    
    # Check if we should auto-refresh
    current_time = time.time()
    if auto_refresh and (current_time - st.session_state.last_refresh) > 30:
        refresh = True
        st.session_state.last_refresh = current_time
    
    # Get data for selected device and time range
    if selected_device:
        # Get time range timestamps
        start_timestamp, end_timestamp = get_time_range_timestamps(time_range)
        
        # Get device data
        df = get_device_data(ref, selected_device, start_timestamp, end_timestamp)
        
        # Render dashboard components
        render_current_readings(df, selected_device)
        render_time_series_charts(df, time_range)
        render_statistics(df)
        render_data_export(df)
    else:
        st.warning("Please select a device to view data")

# Run the application
if __name__ == "__main__":
    main()
