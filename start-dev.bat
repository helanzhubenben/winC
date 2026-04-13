@echo off
setlocal

rem Fishpool local dev launcher.
set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%BACKEND_PYTHON%" (
  echo [ERROR] Backend venv not found: %BACKEND_PYTHON%
  echo Create backend\.venv first.
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
  echo [ERROR] Frontend dependencies not found: %FRONTEND_DIR%\node_modules
  echo Run npm install in frontend first.
  pause
  exit /b 1
)

echo Starting backend window...
start "Fishpool Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && ""%BACKEND_PYTHON%"" manage.py runserver"

echo Starting frontend window...
start "Fishpool Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

echo.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo Two new windows have been opened.

endlocal
