@echo off
echo Deploying fixes to Railway...
echo.
echo Changes made:
echo - Fixed question repetition (LLM now generates unique questions)
echo - Fixed React frontend serving
echo - Updated Groq API key
echo - Enhanced voice detection
echo.
echo Please push these changes to your Railway repository:
echo 1. Commit all changes to git
echo 2. Push to Railway repository
echo 3. Railway will automatically rebuild and deploy
echo.
echo Files changed:
echo - models.py (added messages property)
echo - interviewer.py (fixed dictionary access)
echo - app.py (fixed API route mounting)
echo - Dockerfile (React build support)
echo - nixpacks.toml (Node.js support)
echo.
pause