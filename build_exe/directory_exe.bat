@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0\.."

echo ================================================== > build_exe\pyinstaller_build.log
echo Build started: %DATE% %TIME% >> build_exe\pyinstaller_build.log
echo CWD: %CD% >> build_exe\pyinstaller_build.log
echo. >> build_exe\pyinstaller_build.log
where python >> build_exe\pyinstaller_build.log 2>&1
python -V >> build_exe\pyinstaller_build.log 2>&1
python -c "import sys; print(sys.executable)" >> build_exe\pyinstaller_build.log 2>&1
python -c "import PyInstaller; print('PyInstaller', PyInstaller.__version__)" >> build_exe\pyinstaller_build.log 2>&1
echo ================================================== >> build_exe\pyinstaller_build.log
echo. >> build_exe\pyinstaller_build.log

if exist "Temp_Profiles" rmdir /S /Q "Temp_Profiles"
if exist "Temp_config.ini" del /Q "Temp_config.ini"

if exist "dict_release\mf_timer\Profiles" (
  echo Backing up Profiles...
  xcopy /E /I /Y "dict_release\mf_timer\Profiles" "Temp_Profiles" >nul
) else (
  echo No existing Profiles to back up.
)

if exist "dict_release\mf_timer\mf_config.ini" (
  echo Backing up mf_config.ini...
  copy /Y "dict_release\mf_timer\mf_config.ini" "Temp_config.ini" >nul
) else (
  echo No existing mf_config.ini to back up.
)

echo Cleaning build artifacts...
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"
if exist "dict_release" rmdir /S /Q "dict_release"

echo Running PyInstaller (this can take a while)...
echo PyInstaller command: pyinstaller --clean --noconfirm "build_exe\directory_exe.spec"
echo PyInstaller command: pyinstaller --clean --noconfirm "build_exe\directory_exe.spec" >> build_exe\pyinstaller_build.log

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "& { pyinstaller --clean --noconfirm 'build_exe\directory_exe.spec' 2>&1 | Tee-Object -FilePath 'build_exe\pyinstaller_build.log' -Append; exit $LASTEXITCODE }"

if errorlevel 1 (
  echo.
  echo Build FAILED. See build_exe\pyinstaller_build.log
  echo.
  exit /b 1
)

if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"

if exist "Temp_Profiles" (
  echo Restoring Profiles...
  if not exist "dict_release\mf_timer\Profiles" mkdir "dict_release\mf_timer\Profiles"
  xcopy /E /I /Y "Temp_Profiles" "dict_release\mf_timer\Profiles" >nul
)

if exist "Temp_config.ini" (
  echo Restoring mf_config.ini...
  copy /Y "Temp_config.ini" "dict_release\mf_timer\mf_config.ini" >nul
)

if exist "Temp_Profiles" rmdir /S /Q "Temp_Profiles"
if exist "Temp_config.ini" del /Q "Temp_config.ini"

if exist "dict_release\mf_timer" (
  echo Opening release folder...
  start "" "dict_release\mf_timer"
) else (
  echo Build succeeded but output folder not found where expected.
  echo Check dict_release\mf_timer\
)

echo Build complete: %DATE% %TIME% >> build_exe\pyinstaller_build.log
endlocal
exit /b 0
