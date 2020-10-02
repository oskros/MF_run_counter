rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_run_counter\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_run_counter\dist"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_run_counter\release"
cd "C:\Users\oskro\PycharmProjects\MF_run_counter"
path=C:\Users\oskro\Downloads\WPy32-3850\python-3.8.5;C:\Users\oskro\Downloads\WPy32-3850\python-3.8.5\Scripts
pyinstaller "C:\Users\oskro\PycharmProjects\MF_run_counter\build_exe\onefile_exe.spec" --windowed --onefile --clean --icon="C:\Users\oskro\PycharmProjects\MF_run_counter\media\icon.ico"
start C:\Users\oskro\PycharmProjects\MF_run_counter\release
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_run_counter\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_run_counter\dist"
exit