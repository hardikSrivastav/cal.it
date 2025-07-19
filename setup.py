#!/usr/bin/env python3
"""
Setup script for Calorie Tracking Bot
"""

import os
import sys
import subprocess

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def create_env_file():
    """Create .env file for optional API keys"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print("🔧 Creating .env file for optional API keys...")
        env_content = """# Optional API Keys for Enhanced Nutrition Data
# Get these for better nutrition information

# USDA Food Database API (free)
# Sign up at: https://fdc.nal.usda.gov/api-key-signup.html
USDA_API_KEY=

# Nutritionix API (free tier available)
# Sign up at: https://www.nutritionix.com/business/api
NUTRITIONIX_APP_ID=
NUTRITIONIX_APP_KEY=

# OpenAI API (optional, for advanced food parsing)
# Sign up at: https://platform.openai.com/
OPENAI_API_KEY=
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file")
        print("   You can add optional API keys to this file for better nutrition data")
    else:
        print("✅ .env file already exists")

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "test_bot.py"])
        return True
    except subprocess.CalledProcessError:
        print("❌ Some tests failed")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Calorie Tracking Bot...\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Run tests
    if run_tests():
        print("\n🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the bot: python telegram_bot.py")
        print("2. Open Telegram and find your bot: @it_cal_bot")
        print("3. Send /start to get started")
        print("\nOptional: Add API keys to .env file for better nutrition data")
    else:
        print("\n⚠️  Setup completed with warnings")
        print("Some tests failed, but the bot may still work")
        print("Check the test output above for details")

if __name__ == "__main__":
    main() 