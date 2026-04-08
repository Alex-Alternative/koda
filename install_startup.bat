@echo off
echo Creating Windows startup shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut(\"$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Koda.lnk\"); $s.TargetPath = '%~dp0start.bat'; $s.WorkingDirectory = '%~dp0'; $s.WindowStyle = 7; $s.Description = 'Koda voice-to-text'; $s.Save()"
echo Done! Koda will now start automatically when you log in.
echo.
echo You can also double-click start.bat to launch it manually.
pause
