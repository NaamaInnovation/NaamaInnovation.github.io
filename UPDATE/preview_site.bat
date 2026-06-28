@echo off
cd /d "%~dp0.."
echo Preview server starting at http://127.0.0.1:8123
echo Keep this window open while previewing the website.
echo Press Ctrl+C to stop the server.
python -m http.server 8123
pause
