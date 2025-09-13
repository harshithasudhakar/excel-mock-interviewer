# Render Deployment Guide

## Prerequisites
1. GitHub account
2. Render account (free at render.com)
3. Your GROQ API key

## Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/excel-mock-interviewer.git
git push -u origin main
```

## Step 2: Deploy Backend on Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `excel-interviewer-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variable:
   - **Key**: `GROQ_API_KEY`
   - **Value**: Your actual GROQ API key
6. Click "Create Web Service"

## Step 3: Deploy Frontend on Render
1. Click "New +" → "Static Site"
2. Connect same GitHub repository
3. Configure:
   - **Name**: `excel-interviewer-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
4. Click "Create Static Site"

## Step 4: Update Frontend URL
After backend deploys, you'll get a URL like:
`https://excel-interviewer-api-xyz.onrender.com`

Update the API_BASE in App.jsx to use your actual backend URL.

## Your App URLs
- **Backend API**: https://excel-interviewer-api-xyz.onrender.com
- **Frontend**: https://excel-interviewer-frontend-abc.onrender.com

Share the frontend URL with your friends!