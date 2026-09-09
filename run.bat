@echo off
echo Starting RenewGrid Full-Stack Environment...

:: Start the FastAPI Backend in a new window
echo Starting Backend...
start "RenewGrid Backend" cmd /k "cd backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload"

:: Start the React Frontend in a new window
echo Starting Frontend...
start "RenewGrid Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers have been started in separate windows!
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:5173
echo.
pause
