@echo off
chcp 65001 >nul
echo === LLMProviderMon Windows Build ===
echo.

pip install pyinstaller

pyinstaller --onefile --windowed --collect-all customtkinter --name "LLMProviderMon" main.py

echo.
echo Build complete! Output: dist\LLMProviderMon.exe
pause
