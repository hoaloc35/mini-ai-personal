@echo off
REM ===============================================
REM AI 383 -- Setup cho Windows
REM ===============================================

echo.
echo  +=======================================+
echo  |     AI 383 -- Setup Windows           |
echo  +=======================================+
echo.

REM Kiem tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python chua duoc cai dat!
    echo    Tai Python tai: https://www.python.org/downloads/
    echo    Nho tick "Add Python to PATH" khi cai dat!
    pause
    exit /b 1
)

echo Python da cai dat
echo.

REM Cai dat packages
echo Cai dat Python packages...
pip install -r requirements.txt

REM Tao file .env
if not exist .env (
    echo Tao file .env...
    (
        echo # AI 383 Configuration
        echo # Lay API key mien phi tai: https://aistudio.google.com/apikey
        echo GEMINI_API_KEY=your_api_key_here
        echo.
        echo # Server
        echo HOST=0.0.0.0
        echo PORT=8383
        echo.
        echo # Model
        echo MODEL_NAME=gemini-2.0-flash
        echo.
        echo # === Creative AI Tools (tuy chon) ===
        echo # IMAGE_GEN_API_KEY=your_key_here
        echo # IMAGE_GEN_PROVIDER=gemini
        echo # VIDEO_GEN_API_KEY=your_key_here
        echo # VIDEO_GEN_PROVIDER=runway
        echo # MUSIC_GEN_API_KEY=your_key_here
        echo # MUSIC_GEN_PROVIDER=suno
    ) > .env
    echo Hay mo file .env va them GEMINI_API_KEY!
)

REM Tao thu muc
if not exist data mkdir data
if not exist uploads mkdir uploads
if not exist knowledge_base mkdir knowledge_base

echo.
echo ========================================
echo  Cai dat hoan tat!
echo.
echo  Buoc tiep theo:
echo    1. Mo file .env — them GEMINI_API_KEY
echo    2. Chay: python main.py
echo    3. Mo trinh duyet: http://localhost:8383
echo.
echo  Lay API key mien phi:
echo    https://aistudio.google.com/apikey
echo ========================================
echo.
pause
