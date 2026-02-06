@echo off
echo Starting all News APIs...

echo Starting sdt-api (Port 3000)...
start "Berita Indo API (Next.js)" cmd /k "cd berita-indo-api && npm run dev"

echo Starting api-berita-indonesia (Port 3002)...
start "News API ID (Express)" cmd /k "cd api-berita-indonesia && node src/server.js"

echo Starting cnnindonesia-news-api (Port 5001)...
start "CNN Indonesia API (Flask)" cmd /k "cd cnnindonesia-news-api && venv\Scripts\python main.py"

echo Starting detiknews_api (Port 5002)...
start "Detik News API (Flask)" cmd /k "cd detiknews_api && venv\Scripts\python main.py"

echo All APIs started!
echo ------------------------------------------
echo 1. Berita Indo: http://localhost:3000
echo 2. News API ID: http://localhost:3002
echo 3. CNN API:     http://localhost:5001
echo 4. Detik API:   http://localhost:5002
echo ------------------------------------------
pause
