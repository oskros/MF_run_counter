rmdir /S /Q "C:\Users\sparkie\Desktop\MF_run_counter\build"
rmdir /S /Q "C:\Users\sparkie\Desktop\MF_run_counter\dist"
rmdir /S /Q "C:\Users\sparkie\Desktop\MF_run_counter\release"
cd "C:\Users\sparkie\Desktop\MF_run_counter"
path=C:\Users\oskro\Downloads\WPy64-3830\python-3.8.3.amd64;C:\Users\oskro\Downloads\WPy64-3830\python-3.8.3.amd64\Scripts
pyinstaller "C:\Users\sparkie\Desktop\MF_run_counter\build_exe\onefile_exe.spec" --windowed --onefile --clean --icon="C:\Users\sparkie\Desktop\MF_run_counter\media\icon.ico"
start C:\Users\sparkie\Desktop\MF_run_counter\release
rmdir /S /Q "C:\Users\sparkie\Desktop\MF_run_counter\build"
rmdir /S /Q "C:\Users\sparkie\Desktop\MF_run_counter\dist"
exit