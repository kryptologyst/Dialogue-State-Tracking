#!/usr/bin/env python3
"""
Setup script for Advanced Dialogue State Tracking project.
This script handles installation, configuration, and initial setup.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install --upgrade pip",
        "Upgrading pip"
    ) and run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing Python dependencies"
    )

def download_spacy_model():
    """Download spaCy English model"""
    return run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy English model"
    )

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "data", "static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_database():
    """Initialize the mock database"""
    try:
        from database import MockDatabase
        db = MockDatabase()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def run_tests():
    """Run the test suite"""
    return run_command(
        f"{sys.executable} -m pytest test_dialogue_tracking.py -v",
        "Running test suite"
    )

def main():
    """Main setup function"""
    print("🚀 Advanced Dialogue State Tracking - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Download spaCy model
    if not download_spacy_model():
        print("❌ Failed to download spaCy model")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Initialize database
    if not initialize_database():
        print("❌ Failed to initialize database")
        sys.exit(1)
    
    # Run tests
    print("\n🧪 Running tests...")
    if not run_tests():
        print("⚠️  Some tests failed, but setup can continue")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the demo: python 0182.py")
    print("2. Start the web app: python api.py")
    print("3. Open browser: http://localhost:8000")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
