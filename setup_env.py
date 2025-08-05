#!/usr/bin/env python3
"""
Setup script to create .env file for Gemini AI Chat application
"""

import os

def create_env_file():
    """Create .env file with user input"""
    print("🤖 Gemini AI Chat - Environment Setup")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get API key from user
    print("\n📝 Please enter your Gemini API key:")
    print("Get your API key from: https://makersuite.google.com/app/apikey")
    api_key = input("GEMINI_API_KEY: ").strip()
    
    if not api_key:
        print("❌ API key is required!")
        return
    
    # Get Flask secret key (optional)
    print("\n🔐 Flask Secret Key (optional, press Enter for default):")
    flask_key = input("FLASK_SECRET_KEY: ").strip() or "your-secret-key-here"
    
    # Create .env file
    env_content = f"""# Gemini API Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY={api_key}

# Flask Secret Key (change this in production)
FLASK_SECRET_KEY={flask_key}
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("\n✅ .env file created successfully!")
        print("🔒 Your API key is now securely stored in .env file")
        print("📝 The .env file is automatically ignored by git")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 