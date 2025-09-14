FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a simple startup script
RUN echo '#!/bin/bash\nexec python main.py' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]