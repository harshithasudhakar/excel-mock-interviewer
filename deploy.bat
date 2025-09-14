@echo off
echo Building React frontend...
cd frontend
call npm run build
cd ..

echo Deploying to Railway...
echo Please manually push to your Railway repository or use Railway CLI
echo Files are ready for deployment with React frontend
pause