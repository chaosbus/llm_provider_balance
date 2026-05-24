#!/usr/bin/env bash
set -euo pipefail

echo "=== LLMProviderMon Linux Build ==="
echo

pip install pyinstaller

pyinstaller --onefile --windowed --collect-all customtkinter --name "LLMProviderMon" main.py

echo
echo "Build complete! Output: dist/LLMProviderMon"
