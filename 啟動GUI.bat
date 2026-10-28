@echo off
chcp 65001 >nul
cd /d "%~dp0"
python app.py
if errorlevel 1 (
  echo.
  echo 若提示找不到 python，請先安裝 Python 並勾選 Add to PATH。
  echo 或先執行：pip install -r requirements.txt
  pause
)
