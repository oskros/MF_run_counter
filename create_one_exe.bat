rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\dist"
cd "C:\Users\oskro\PycharmProjects\MF_counter_releases"
path=C:\Users\oskro\Downloads\WPy-3701\python-3.7.0.amd64;C:\Users\oskro\Downloads\WPy-3701\python-3.7.0.amd64\Scripts
pyinstaller "C:\Users\oskro\PycharmProjects\MF_counter_releases\mf_timer_onefile.spec" --windowed --onefile --clean --icon="C:\Users\oskro\PycharmProjects\MF_counter_releases\icon.ico"
start C:\Users\oskro\PycharmProjects\MF_counter_releases\release
exit