@echo off
echo Setting up Excel Mock Interviewer for deployment...

echo.
echo 1. Make sure you have:
echo    - GitHub account
echo    - Render account (render.com)
echo    - Your GROQ API key ready

echo.
echo 2. Initialize Git repository...
git init
git add .
git commit -m "Initial deployment setup"

echo.
echo 3. Next steps:
echo    - Create GitHub repository
echo    - Push code: git remote add origin YOUR_REPO_URL
echo    - Follow DEPLOYMENT.md instructions

echo.
echo Ready for deployment! Check DEPLOYMENT.md for complete instructions.
pause