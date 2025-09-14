FROM python:3.11-slim

WORKDIR /app

# Install Node.js for React build
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Build React frontend
RUN cd frontend && npm install && npm run build

# Create a simple startup script
RUN echo '#!/bin/bash\nexec python main.py' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]