#!/usr/bin/env python3
import os
import subprocess
import sys

port = os.environ.get("PORT", "8000")
print(f"Starting on port: {port}")
print(f"GROQ_API_KEY set: {'Yes' if os.environ.get('GROQ_API_KEY') else 'No'}")

subprocess.run([
    sys.executable, "-m", "uvicorn", 
    "app:app", 
    "--host", "0.0.0.0", 
    "--port", port
])