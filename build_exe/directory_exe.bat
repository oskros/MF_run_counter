rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\dist"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\dict_release"
cd "C:\Users\oskro\PycharmProjects\MF_counter_releases"
path=C:\Users\oskro\Downloads\WPy-3701\python-3.7.0.amd64;C:\Users\oskro\Downloads\WPy-3701\python-3.7.0.amd64\Scripts
pyinstaller "C:\Users\oskro\PycharmProjects\MF_counter_releases\build_exe\directory_exe.spec" --windowed --clean --icon="C:\Users\oskro\PycharmProjects\MF_counter_releases\media\icon.ico"
start C:\Users\oskro\PycharmProjects\MF_counter_releases\dict_release\mf_timer
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter_releases\dist"
exit