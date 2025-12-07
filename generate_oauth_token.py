"""
Generate a unified OAuth token for Gmail and Google Sheets.
This creates a single token.json that works for both services.
"""
import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from src.config import settings

# Combined scopes for both Gmail and Sheets
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/spreadsheets'
]

def generate_token():
    creds = None
    token_path = "token.json"
    
    # Check if token already exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print(f"Found existing token at {token_path}")
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not settings.gmail_credentials_path or not os.path.exists(settings.gmail_credentials_path):
                print("ERROR: GMAIL_CREDENTIALS_PATH not set or credentials file not found.")
                print("Please set up your OAuth credentials first.")
                return
            
            print(f"Starting OAuth flow with credentials from: {settings.gmail_credentials_path}")
            print("This will open a browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.gmail_credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(token_path, "w") as token:
            token.write(creds.to_json())
        print(f"\n✅ Token saved to {token_path}")
    else:
        print("✅ Token is valid!")
    
    # Display token info
    token_data = json.loads(creds.to_json())
    print("\n📋 Token scopes:", token_data.get('scopes'))
    print("\n💡 For cloud deployment, copy this token content to your environment variable:")
    print(f"   GMAIL_TOKEN_JSON='{creds.to_json()}'")
    print("\n💡 Since this token has both scopes, you can use the same value for:")
    print("   GOOGLE_SHEETS_TOKEN_JSON='{same value}'")

if __name__ == "__main__":
    print("Starting OAuth token generation...")
    generate_token()
