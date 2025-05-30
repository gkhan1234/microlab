"""
Firebase Setup Helper Script

This script helps set up Firebase credentials for the ESP32 Environmental Monitoring Dashboard.
It guides the user through the process of creating a firebase_credentials.json file
and setting up the appropriate database rules.

Usage:
    python setup_firebase.py

Author: Generated by Cline
Date: March 25, 2025
"""

import json
import os
import sys
import webbrowser
from pathlib import Path

def print_header():
    """Print the script header."""
    print("\n" + "=" * 80)
    print("Firebase Setup Helper for ESP32 Environmental Monitoring Dashboard".center(80))
    print("=" * 80 + "\n")

def print_step(step_num, title):
    """Print a step header."""
    print(f"\nSTEP {step_num}: {title}")
    print("-" * 50)

def get_user_input(prompt, default=None):
    """Get input from the user with an optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def open_firebase_console():
    """Open the Firebase console in the default web browser."""
    print_step(1, "Opening Firebase Console")
    print("Opening the Firebase Console in your web browser...")
    print("If it doesn't open automatically, go to: https://console.firebase.google.com/")
    
    try:
        webbrowser.open("https://console.firebase.google.com/")
        input("\nPress Enter once you've accessed the Firebase Console...")
    except Exception as e:
        print(f"Error opening browser: {e}")
        print("Please manually navigate to: https://console.firebase.google.com/")
        input("\nPress Enter to continue once you've accessed the Firebase Console...")

def guide_service_account_creation():
    """Guide the user through creating a service account."""
    print_step(2, "Creating a Service Account")
    print("To set up Firebase authentication, you need to create a service account:")
    print("1. In the Firebase Console, select your project")
    print("2. Click the gear icon (⚙️) near the top left to open Project settings")
    print("3. Go to the 'Service accounts' tab")
    print("4. Click 'Generate new private key'")
    print("5. Save the JSON file")
    
    input("\nPress Enter once you've downloaded the service account key file...")

def create_credentials_file():
    """Create the firebase_credentials.json file."""
    print_step(3, "Setting Up Credentials File")
    
    # Ask if the user wants to use an existing key file or enter details manually
    choice = get_user_input("Do you want to use an existing key file (1) or enter details manually (2)?", "1")
    
    if choice == "1":
        # Use existing key file
        file_path = get_user_input("Enter the path to your downloaded service account key file")
        
        try:
            with open(file_path, 'r') as f:
                credentials = json.load(f)
            
            # Save to firebase_credentials.json
            with open('firebase_credentials.json', 'w') as f:
                json.dump(credentials, f, indent=2)
            
            print("\n✅ Successfully created firebase_credentials.json")
            
            # Extract database URL
            if 'projectId' in credentials:
                project_id = credentials['projectId']
                default_db_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
            else:
                default_db_url = "https://your-project-id-default-rtdb.firebaseio.com/"
            
            # Ask for database URL
            db_url = get_user_input("Enter your Firebase Realtime Database URL", default_db_url)
            
            # Update the credentials file with the database URL
            credentials['databaseURL'] = db_url
            
            with open('firebase_credentials.json', 'w') as f:
                json.dump(credentials, f, indent=2)
            
            print(f"\n✅ Added database URL: {db_url}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Failed to create credentials file. Please try again.")
            return False
    
    else:
        # Manual entry
        print("\nPlease enter the following details from your service account key file:")
        
        project_id = get_user_input("Project ID")
        private_key_id = get_user_input("Private Key ID")
        client_email = get_user_input("Client Email")
        
        # Create a simplified credentials file
        credentials = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": private_key_id,
            "client_email": client_email,
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": ""
        }
        
        # Ask for private key (simplified)
        print("\nFor the private key, you should copy it from the JSON file.")
        print("It starts with '-----BEGIN PRIVATE KEY-----' and ends with '-----END PRIVATE KEY-----'")
        private_key = get_user_input("Enter 'skip' to skip this step (not recommended)", "skip")
        
        if private_key != "skip":
            credentials["private_key"] = private_key
        
        # Ask for database URL
        default_db_url = f"https://{project_id}-default-rtdb.firebaseio.com/"
        db_url = get_user_input("Enter your Firebase Realtime Database URL", default_db_url)
        credentials['databaseURL'] = db_url
        
        # Save to firebase_credentials.json
        try:
            with open('firebase_credentials.json', 'w') as f:
                json.dump(credentials, f, indent=2)
            
            print("\n✅ Successfully created firebase_credentials.json")
            print("⚠️ Note: This is a simplified version. For production use, it's better to use the downloaded key file.")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Failed to create credentials file. Please try again.")
            return False
    
    return True

def guide_database_rules():
    """Guide the user through setting up database rules."""
    print_step(4, "Setting Up Database Rules")
    print("For your Firebase Realtime Database, you need to set appropriate security rules:")
    print("\nFor development/testing, you can use:")
    print("""
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
""")
    print("For production, consider more restrictive rules like:")
    print("""
{
  "rules": {
    "readings": {
      "$device_id": {
        ".read": true,
        ".write": "auth != null"
      }
    }
  }
}
""")
    
    print("\nTo set these rules:")
    print("1. In the Firebase Console, go to your project")
    print("2. Select 'Realtime Database' from the left menu")
    print("3. Click on the 'Rules' tab")
    print("4. Enter your rules and click 'Publish'")
    
    input("\nPress Enter once you've set up your database rules...")

def verify_setup():
    """Verify the setup is complete."""
    print_step(5, "Verifying Setup")
    
    # Check if firebase_credentials.json exists
    if os.path.exists('firebase_credentials.json'):
        print("✅ firebase_credentials.json file found")
        
        # Verify file contains required fields
        try:
            with open('firebase_credentials.json', 'r') as f:
                credentials = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key_id', 'client_email']
            missing_fields = [field for field in required_fields if field not in credentials]
            
            if missing_fields:
                print(f"⚠️ Warning: Missing fields in credentials file: {', '.join(missing_fields)}")
            else:
                print("✅ Credentials file contains required fields")
            
            if 'databaseURL' in credentials:
                print(f"✅ Database URL: {credentials['databaseURL']}")
            else:
                print("⚠️ Warning: No database URL found in credentials file")
                
        except Exception as e:
            print(f"❌ Error reading credentials file: {e}")
    else:
        print("❌ firebase_credentials.json file not found")
        return False
    
    return True

def print_next_steps():
    """Print next steps for the user."""
    print_step(6, "Next Steps")
    print("Your Firebase setup is complete! Here's what to do next:")
    print("\n1. Run the dashboard application:")
    print("   streamlit run dashboard.py")
    print("\n2. If you encounter any issues:")
    print("   - Check the dashboard_README.md file for troubleshooting tips")
    print("   - Verify your Firebase project is properly configured")
    print("   - Ensure your ESP32 device is sending data in the correct format")
    
    print("\nThe dashboard will automatically connect to your Firebase database")
    print("or run in demo mode if it can't connect.")

def main():
    """Main function to run the setup process."""
    print_header()
    
    print("This script will help you set up Firebase credentials for the ESP32 Environmental Monitoring Dashboard.")
    print("It will guide you through creating a service account and setting up database rules.")
    
    proceed = get_user_input("Do you want to proceed? (y/n)", "y").lower()
    if proceed != "y":
        print("\nSetup cancelled. You can run this script again later.")
        return
    
    # Step 1: Open Firebase Console
    open_firebase_console()
    
    # Step 2: Guide Service Account Creation
    guide_service_account_creation()
    
    # Step 3: Create Credentials File
    if not create_credentials_file():
        print("\nFailed to create credentials file. Please try again later.")
        return
    
    # Step 4: Guide Database Rules
    guide_database_rules()
    
    # Step 5: Verify Setup
    verify_setup()
    
    # Step 6: Print Next Steps
    print_next_steps()
    
    print("\n" + "=" * 80)
    print("Setup Complete!".center(80))
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
