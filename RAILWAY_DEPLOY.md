# Railway Deployment - Super Simple! 🚀

## Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/excel-mock-interviewer.git
git push -u origin main
```

## Step 2: Deploy Backend on Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Select your `excel-mock-interviewer` repository
5. Railway auto-detects Python and deploys!
6. Add environment variable:
   - Key: `GROQ_API_KEY`
   - Value: api key

## Step 3: Get Your Backend URL
After deployment, Railway gives you a URL like:
`https://excel-interviewer-api-production.up.railway.app`

## Step 4: Deploy Frontend on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Select your repository
5. Set:
   - Framework: Create React App
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
6. Deploy!

## Step 5: Update Frontend API URL
Update `frontend/src/App.jsx` line 4 with your actual Railway URL:
```javascript
const API_BASE = process.env.NODE_ENV === 'production' 
  ? 'https://YOUR-ACTUAL-RAILWAY-URL.up.railway.app' 
  : 'http://localhost:8000';
```

## Done! 🎉
Your friends can use: `https://your-app.vercel.app`

**Total time: ~10 minutes**