cd ..
rmdir /S /Q "build"
rmdir /S /Q "dist"
rmdir /S /Q "release"
path=%PATH%;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\;%SYSTEMROOT%\System32\downlevel;
pyinstaller "build_exe\onefile_exe.spec"
start release
rmdir /S /Q "build"
rmdir /S /Q "dist"
exit