#!/bin/bash
set -e
echo "Starting Excel Mock Interviewer..."
echo "PORT: ${PORT:-8000}"
echo "GROQ_API_KEY set: $([ -n "$GROQ_API_KEY" ] && echo "Yes" || echo "No")"
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}