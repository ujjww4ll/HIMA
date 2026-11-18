@echo off
setlocal
set PY="%~dp0.venv\Scripts\python.exe"

if not exist %PY% (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe
    echo Run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    exit /b 1
)

if /I "%1"=="demo" (
    %PY% "%~dp0run_pipeline.py" --demo
    exit /b %ERRORLEVEL%
)

if /I "%1"=="fast" (
    %PY% "%~dp0run_pipeline.py" --skip-ingest
    exit /b %ERRORLEVEL%
)

if /I "%1"=="test" (
    %PY% -m pytest -v
    exit /b %ERRORLEVEL%
)

if /I "%1"=="api" (
    %PY% -m src.api.predict
    exit /b %ERRORLEVEL%
)

if /I "%1"=="web" (
    %PY% -m src.api.predict
    exit /b %ERRORLEVEL%
)

%PY% "%~dp0run_pipeline.py"
exit /b %ERRORLEVEL%

