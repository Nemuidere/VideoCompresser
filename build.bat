@echo off
echo Instalowanie/Aktualizowanie wymagan (w tym customtkinter)...
python -m pip install --upgrade pyinstaller ffmpeg-python customtkinter

echo Czyszczenie starych buildow...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo Budowanie programu .exe (Modern UI)...
:: Dodano --collect-all customtkinter aby zalaczyc motywy graficzne
python -m PyInstaller --noconsole --onefile --name "VideoCompressorPro" --collect-all customtkinter --icon=NONE main.py

echo.
echo ========================================================
echo SUKCES! 
echo Program znajduje sie w folderze: dist/VideoCompressorPro.exe
echo ========================================================
pause