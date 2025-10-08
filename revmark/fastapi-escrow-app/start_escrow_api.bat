@echo off
echo ==========================================
echo   RevMark FastAPI Escrow System
echo ==========================================
echo.
echo Starting the escrow API server...
echo.

cd /d "C:\Users\Stamo\RevMark\revmark\fastapi-escrow-app"

echo API will be available at:
echo   📚 API Docs: http://localhost:8001/docs
echo   🔧 ReDoc: http://localhost:8001/redoc  
echo   ❤️  Health: http://localhost:8001/health
echo.
echo Press Ctrl+C to stop the server
echo.

"C:\Users\Stamo\RevMark\revmark\fastapi-escrow-app\fastapi_venv\Scripts\python.exe" run.py

pause