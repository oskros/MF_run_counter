@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ------------------------------------------------------------------
REM Build hygiene + safety
REM ------------------------------------------------------------------

REM Move to repo root (your script currently starts in build_exe or similar)
cd /d "%~dp0\.."

REM Optional: if you have a venv, activate it here (uncomment and adjust)
REM call .venv\Scripts\activate.bat

REM Record build info (helps detect wrong Python/venv)
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

REM ------------------------------------------------------------------
REM Backup existing user data from previous release (if present)
REM ------------------------------------------------------------------

REM Clean old temp backups first
if exist "Temp_Profiles" rmdir /S /Q "Temp_Profiles"
if exist "Temp_config.ini" del /Q "Temp_config.ini"

REM Only backup if previous build exists
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

REM ------------------------------------------------------------------
REM Clean build artifacts thoroughly
REM ------------------------------------------------------------------

echo Cleaning build artifacts...
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"
if exist "dict_release" rmdir /S /Q "dict_release"

REM ------------------------------------------------------------------
REM Run PyInstaller with extra hygiene and logging
REM ------------------------------------------------------------------

echo Running PyInstaller...
echo PyInstaller command: pyinstaller --clean --noconfirm "build_exe\directory_exe.spec" >> build_exe\pyinstaller_build.log
pyinstaller --clean --noconfirm "build_exe\directory_exe.spec" >> build_exe\pyinstaller_build.log 2>&1

if errorlevel 1 (
  echo.
  echo Build FAILED. See build_exe\pyinstaller_build.log
  echo.
  REM Keep temp backups for manual recovery
  exit /b 1
)

REM PyInstaller often recreates build/dist; remove if you truly don't want them
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"

REM ------------------------------------------------------------------
REM Restore user data into the new release (if we backed it up)
REM ------------------------------------------------------------------

if exist "Temp_Profiles" (
  echo Restoring Profiles...
  if not exist "dict_release\mf_timer\Profiles" mkdir "dict_release\mf_timer\Profiles"
  xcopy /E /I /Y "Temp_Profiles" "dict_release\mf_timer\Profiles" >nul
)

if exist "Temp_config.ini" (
  echo Restoring mf_config.ini...
  copy /Y "Temp_config.ini" "dict_release\mf_timer\mf_config.ini" >nul
)

REM ------------------------------------------------------------------
REM Cleanup temp backups
REM ------------------------------------------------------------------

if exist "Temp_Profiles" rmdir /S /Q "Temp_Profiles"
if exist "Temp_config.ini" del /Q "Temp_config.ini"

REM ------------------------------------------------------------------
REM Launch the built app (optional)
REM ------------------------------------------------------------------

if exist "dict_release\mf_timer\mf_timer.exe" (
  echo Starting mf_timer.exe...
  start "" "dict_release\mf_timer\mf_timer.exe"
) else (
  echo Build succeeded but mf_timer.exe not found where expected.
  echo Check dict_release\mf_timer\
)

echo Build complete: %DATE% %TIME% >> build_exe\pyinstaller_build.log
endlocal
exit /b 0
