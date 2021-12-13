rmdir /S /Q Temp_Profiles
del Temp_config.ini
echo d | xcopy dict_release\mf_timer\Profiles Temp_Profiles
echo f | xcopy dict_release\mf_timer\mf_config.ini Temp_Profiles\Temp_config.ini
rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q dict_release
pyinstaller directory_exe.spec --windowed --clean
rmdir /S /Q build
rmdir /S /Q dist
echo d | xcopy Temp_Profiles dict_release\mf_timer\Profiles
echo f | xcopy Temp_config.ini dict_release\mf_timer\mf_config.ini
rmdir /S /Q Temp_Profiles
del Temp_config.ini
exit