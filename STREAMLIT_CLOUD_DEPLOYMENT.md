# Deploying to Streamlit Cloud - Step by Step Guide

This guide will walk you through the process of deploying your ESP32 Environmental Monitoring Dashboard to Streamlit Cloud for free.

## Why Streamlit Cloud?

- **Free hosting** for public apps
- **No server management** required
- **Automatic updates** when you update your GitHub repository
- **Share with anyone** using a public URL
- **Custom domain** support (on paid plans)

## Prerequisites

- GitHub account
- Your ESP32 Environmental Monitoring Dashboard code
- Firebase project with Realtime Database

## Step 1: Prepare Your Repository

1. Create a new repository on GitHub
2. Add the following files to your repository:
   - `dashboard.py` (main application)
   - `requirements.txt` (dependencies)
   - `.streamlit/config.toml` (configuration)
   - `.gitignore` (optional, but recommended)

Example `.gitignore` file:
```
# Streamlit secrets
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Firebase
firebase_credentials.json

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
```

## Step 2: Create a Streamlit Cloud Account

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Click "Sign up" if you don't have an account
3. You can sign up with your GitHub account for easier integration

## Step 3: Deploy Your App

1. From your Streamlit Cloud dashboard, click "New app"
2. Connect to your GitHub repository:
   - Select the repository containing your dashboard
   - Select the branch (usually `main`)
   - Set the main file path to `dashboard.py`
3. Click "Deploy"

Your app will now build and deploy. This may take a few minutes.

## Step 4: Set Up Secrets

Your Firebase credentials need to be securely stored as Streamlit secrets:

1. In your deployed app, click the three-dot menu (⋮) in the top right
2. Select "Settings"
3. Click on "Secrets"
4. Add your Firebase credentials in TOML format:

```toml
[firebase]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
Your private key here (multi-line)
-----END PRIVATE KEY-----"""
client_email = "your-service-account-email@your-project-id.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project-id.iam.gserviceaccount.com"
database_url = "https://your-project-id-default-rtdb.firebaseio.com/"
```

5. Click "Save"
6. Reboot your app by clicking the three-dot menu (⋮) and selecting "Reboot app"

## Step 5: Test Your Deployed App

1. Your app is now live at a URL like `https://username-repo-name-dashboard-randomstring.streamlit.app/`
2. Test all functionality to ensure it's working correctly:
   - Device selection
   - Time range selection
   - Data visualization
   - Export functionality

## Step 6: Share Your Dashboard

1. Copy your app's URL
2. Share it with anyone who needs access to your environmental monitoring data
3. The dashboard will automatically update as new data is sent to your Firebase database

## Troubleshooting

If your app isn't working correctly:

1. **Check the logs**: Click the three-dot menu (⋮) and select "View app logs"
2. **Verify secrets**: Make sure your Firebase credentials are correctly formatted
3. **Check Firebase rules**: Ensure your Firebase database allows read access
4. **Update dependencies**: Make sure all required packages are in your requirements.txt file
5. **Check for errors**: Look for any error messages in the app or logs

## Updating Your App

To update your dashboard:

1. Make changes to your code in your local repository
2. Commit and push to GitHub
3. Streamlit Cloud will automatically rebuild and redeploy your app

## Free Tier Limitations

Streamlit Cloud's free tier includes:

- Public apps only (no password protection)
- Up to 3 apps per account
- Apps sleep after inactivity (wake on access)
- Shared CPU and memory resources
- No custom domains

For more features, you can upgrade to a paid plan.

## Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [Streamlit Secrets Management](https://docs.streamlit.io/library/advanced-features/secrets-management)
- [Streamlit Components](https://docs.streamlit.io/library/components)
- [Streamlit Forum](https://discuss.streamlit.io/)
