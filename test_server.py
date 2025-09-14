import os
print("React build exists:", os.path.exists("frontend/build/index.html"))
print("Static HTML exists:", os.path.exists("static/index.html"))

# Test which one gets served
from app import app
import uvicorn

if __name__ == "__main__":
    print("Starting server to test frontend...")
    uvicorn.run(app, host="127.0.0.1", port=8000)