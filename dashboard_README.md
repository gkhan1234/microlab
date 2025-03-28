# ESP32 Environmental Monitoring Dashboard

This Streamlit application visualizes environmental monitoring data from ESP32 devices stored in a Firebase Realtime Database. It provides real-time data display, time-series charts, statistical analysis, and data export functionality.

## Features

- Authentication and connection to Firebase Realtime Database
- Device selector to choose which environmental monitor to display
- Time range selector (Last Hour, Last Day, Last Week, Last Month)
- Real-time data display showing current temperature, humidity, light, and soil moisture readings
- Time-series charts for each environmental parameter using Plotly
- Statistical analysis section showing min, max, average, and trends
- Data export functionality to download readings as CSV
- Sample data generator for testing when no real data is available
- Responsive design that works on desktop and mobile browsers
- Proper error handling for database connection issues

## Prerequisites

- Python 3.8 or higher
- Firebase Realtime Database (set up with your ESP32 environmental monitoring system)
- GitHub account (for Streamlit Cloud deployment)
- Streamlit Cloud account (free tier available)

## Deployment Options

You have two options for running this dashboard:

### Option 1: Local Deployment

1. Clone this repository or download the files
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Firebase credentials (see Firebase Setup section below)
4. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```
   The dashboard will open in your default web browser at http://localhost:8501

### Option 2: Streamlit Cloud Deployment (Recommended)

Deploy your dashboard to Streamlit Cloud for free, making it accessible from anywhere:

1. Create a GitHub repository and push your dashboard code to it
2. Sign up for a free Streamlit Cloud account at https://streamlit.io/cloud
3. Connect your GitHub repository to Streamlit Cloud
4. Set up your Firebase credentials as secrets (see Streamlit Cloud Setup section below)
5. Deploy your dashboard with one click

## Firebase Setup

### Option 1: Anonymous Access (Development/Testing)

1. Go to your Firebase console: https://console.firebase.google.com/
2. Select your project (e.g., microlab-data)
3. Go to "Realtime Database" in the left sidebar
4. Click on "Rules" tab
5. For development/testing purposes, set rules to allow anonymous access:
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```
6. Click "Publish" to save these rules

### Option 2: Authentication with Service Account

1. Go to your Firebase console: https://console.firebase.google.com/
2. Select your project
3. Go to Project Settings (gear icon) > Service accounts
4. Click "Generate new private key"
5. Save the JSON file (you'll need its contents for Streamlit Cloud secrets)

## Streamlit Cloud Setup

### Step 1: Create a GitHub Repository

1. Create a new repository on GitHub
2. Upload the following files to your repository:
   - dashboard.py
   - requirements.txt
   - .streamlit/config.toml (create this directory and file)

### Step 2: Create a Streamlit Cloud Account

1. Go to https://streamlit.io/cloud
2. Sign up for a free account (you can use your GitHub account to sign in)

### Step 3: Deploy Your Dashboard

1. From the Streamlit Cloud dashboard, click "New app"
2. Connect to your GitHub repository
3. Set the main file path to "dashboard.py"
4. Click "Deploy"

### Step 4: Set Up Secrets for Firebase

1. In your deployed app, click the "Settings" menu (⋮)
2. Select "Secrets"
3. Add your Firebase credentials in the following format:

```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
database_url = "https://your-project-id-default-rtdb.firebaseio.com/"
```

Replace all values with those from your Firebase service account key file.

## Demo Mode

If no Firebase credentials are provided, the dashboard will run in demo mode with sample data. This is useful for testing the interface without a Firebase connection.

## Data Format

The dashboard expects data in the Firebase Realtime Database to be structured as follows:

```
/readings
  /device_id_1
    /reading_1
      timestamp: 1616876400
      readings:
        temperature: 25
        humidity: 60
        light_level: 75.5
        soil_moisture: 42.3
    /reading_2
      ...
  /device_id_2
    ...
```

## Customization

You can customize the dashboard by modifying the following:

- Update the Firebase URL in the `initialize_firebase()` function
- Adjust the time ranges in the `get_time_range_timestamps()` function
- Modify the chart colors and styles in the rendering functions
- Add additional environmental parameters by updating the data processing functions

## Troubleshooting

- If you encounter connection issues, check your Firebase credentials and database rules
- For visualization problems, ensure your data format matches the expected structure
- If running in demo mode, verify that the sample data generator is producing appropriate values
- For Streamlit Cloud issues, check the deployment logs and verify your secrets are correctly set

## Educational Use

This dashboard is designed for educational purposes, with clear labels and explanations suitable for classroom use. It focuses on making environmental data accessible and meaningful.

## License

This project is provided for educational purposes. Feel free to modify and use it for your own projects.
