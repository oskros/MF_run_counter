@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0\.."

set "SPEC=build_exe\onefile_exe.spec"
set "LOG=build_exe\pyinstaller_onefile_build.log"

echo ================================================== > "%LOG%"
echo Build started: %DATE% %TIME% >> "%LOG%"
echo CWD: %CD% >> "%LOG%"
echo. >> "%LOG%"
where python >> "%LOG%" 2>&1
python -V >> "%LOG%" 2>&1
python -c "import sys; print(sys.executable)" >> "%LOG%" 2>&1
python -c "import PyInstaller; print('PyInstaller', PyInstaller.__version__)" >> "%LOG%" 2>&1
echo ================================================== >> "%LOG%"
echo. >> "%LOG%"

REM Hard clean of build output
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"
if exist "release" rmdir /S /Q "release"

REM Build (force clean analysis + no prompts)
echo Running PyInstaller... >> "%LOG%"
pyinstaller --clean --noconfirm "%SPEC%" >> "%LOG%" 2>&1

if errorlevel 1 (
  echo.
  echo Onefile build FAILED. See "%LOG%"
  exit /b 1
)

REM Optional: remove build/dist again after success
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"

REM Launch the output folder (or the exe if you prefer)
if exist "release" (
  start "" "release"
)

echo Build complete: %DATE% %TIME% >> "%LOG%"
endlocal
exit /b 0
