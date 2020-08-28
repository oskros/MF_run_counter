rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\dist"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\release"
cd "C:\Users\oskro\PycharmProjects\MF_counter_releases"
path=%PATH%C:\Users\oskro\Downloads\WPy64-3830\python-3.8.3.amd64;C:\Users\oskro\Downloads\WPy64-3830\python-3.8.3.amd64\Scripts
pyinstaller "C:\Users\oskro\PycharmProjects\MF_counter_releases\build_exe\onefile_exe.spec" --windowed --onefile --clean --icon="C:\Users\oskro\PycharmProjects\MF_counter_releases\media\icon.ico"
start C:\Users\oskro\PycharmProjects\MF_counter_releases\release
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\dist"
exit