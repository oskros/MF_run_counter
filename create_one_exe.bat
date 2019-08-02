rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter\build"
rmdir /S /Q "C:\Users\oskro\PycharmProjects\MF_counter\dist"
path=C:\Users\oskro\Downloads\WPy-3701\python-3.7.0.amd64;C:\Users\oskro\Downloads\WPy-3701\python-3.7.0.amd64\Scripts
pyinstaller "C:\Users\oskro\PycharmProjects\MF_counter\mf_timer_onefile.spec" -w -F
exit