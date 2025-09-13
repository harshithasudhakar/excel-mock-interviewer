#!/usr/bin/env python3
"""
Quick start script for Excel Mock Interviewer
"""
import subprocess
import sys
import os

def main():
    print("🚀 Starting Excel Mock Interviewer...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Please create one with your OPENAI_API_KEY")
        print("   Copy .env.example to .env and add your API key")
        return
    
    # Start Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Interview system stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")

if __name__ == "__main__":
    main()