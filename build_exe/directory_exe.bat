cd ..
rmdir /S /Q "Temp_Profiles"
del "Temp_config.ini"
echo d | xcopy "dict_release\mf_timer\Profiles" "Temp_Profiles"
echo f | xcopy "dict_release\mf_timer\mf_config.ini" "Temp_config.ini"
rmdir /S /Q "build"
rmdir /S /Q "dist"
rmdir /S /Q "dict_release"
path=%PATH%;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem;%SYSTEMROOT%\System32\WindowsPowerShell\v1.0\;%SYSTEMROOT%\System32\downlevel;
pyinstaller "build_exe\directory_exe.spec"
rmdir /S /Q "build"
rmdir /S /Q "dist"
start dict_release\mf_timer
echo d | xcopy "Temp_Profiles" "dict_release\mf_timer\Profiles"
echo f | xcopy "Temp_config.ini" "dict_release\mf_timer\mf_config.ini"
rmdir /S /Q "Temp_Profiles"
del "Temp_config.ini"
exit