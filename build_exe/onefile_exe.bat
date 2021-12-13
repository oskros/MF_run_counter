rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q release
pyinstaller onefile_exe.spec --windowed --onefile --clean --icon=%cd%\..\media\icon.ico
rmdir /S /Q build
rmdir /S /Q dist
exit