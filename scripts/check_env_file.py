#!/usr/bin/env python3
"""
Script to check the .env file contents and verify Alpaca credentials.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check the .env file and display Alpaca credentials."""
    
    print("Checking .env File and Alpaca Credentials")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path("config/.env")
    if not env_file.exists():
        print(f"❌ {env_file} does not exist!")
        print("Please create the .env file with your Alpaca credentials.")
        return False
    
    print(f"✅ Found {env_file}")
    
    # Load the .env file
    load_dotenv(env_file, override=True)
    
    # Get credentials from environment
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    print(f"\nAlpaca Credentials from .env file:")
    print(f"API Key: {api_key}")
    print(f"Secret Key: {secret_key}")
    
    if not api_key:
        print("❌ ALPACA_API_KEY not found in .env file")
        return False
    
    if not secret_key:
        print("❌ ALPACA_SECRET_KEY not found in .env file")
        return False
    
    # Check API key format
    print(f"\nAPI Key Analysis:")
    print(f"Length: {len(api_key)}")
    print(f"Starts with 'PK': {api_key.startswith('PK')}")
    print(f"Starts with 'AK': {api_key.startswith('AK')}")
    
    if api_key.startswith('PK'):
        print("✅ API key format is correct for paper trading")
    elif api_key.startswith('AK'):
        print("⚠️  API key format suggests live trading")
    else:
        print("❌ API key format is unexpected")
    
    return True

def test_credentials():
    """Test the credentials from the .env file."""
    
    print(f"\nTesting Credentials")
    print("=" * 30)
    
    # Load environment variables
    env_file = Path("config/.env")
    load_dotenv(env_file, override=True)
    
    api_key = os.getenv('ALPACA_API_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Credentials not found in environment")
        return False
    
    try:
        import requests
        
        # Test paper trading endpoint
        url = "https://paper-api.alpaca.markets/v2/account"
        headers = {
            "APCA-API-KEY-ID": api_key,
            "APCA-API-SECRET-KEY": secret_key
        }
        
        print(f"Testing connection to: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Connection successful!")
            account_data = response.json()
            print(f"Account ID: {account_data.get('id', 'N/A')}")
            print(f"Status: {account_data.get('status', 'N/A')}")
            return True
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Authentication failed")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing credentials: {str(e)}")
        return False

def show_env_file_contents():
    """Show the contents of the .env file."""
    
    print(f"\n.env File Contents")
    print("=" * 30)
    
    env_file = Path("config/.env")
    if not env_file.exists():
        print("❌ .env file not found")
        return
    
    try:
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Show only Alpaca-related lines for security
        lines = content.split('\n')
        alpaca_lines = [line for line in lines if 'ALPACA' in line.upper()]
        
        if alpaca_lines:
            print("Alpaca configuration lines:")
            for line in alpaca_lines:
                if 'SECRET' in line.upper():
                    # Mask the secret key for security
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        print(f"{parts[0]}=***{parts[1][-4:] if len(parts[1]) > 4 else '***'}")
                else:
                    print(line)
        else:
            print("No Alpaca configuration found in .env file")
            
    except Exception as e:
        print(f"❌ Error reading .env file: {str(e)}")

if __name__ == "__main__":
    print("Alpaca Credentials Checker")
    print("=" * 50)
    
    # Check .env file
    env_ok = check_env_file()
    
    if env_ok:
        # Show file contents
        show_env_file_contents()
        
        # Test credentials
        test_credentials()
        
        print(f"\n" + "=" * 50)
        print("Check complete!")
        
        if env_ok:
            print("\nIf you're still getting 403 errors:")
            print("1. Double-check your API keys in the Alpaca dashboard")
            print("2. Make sure you copied the keys correctly")
            print("3. Try regenerating the keys again")
            print("4. Check if your account is active and not restricted")
    else:
        print("\nPlease fix the .env file issues before testing credentials.") 