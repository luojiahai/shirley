@echo off

set DIR=%~dp0
set PYTHON_DIR=%DIR%\python
set PATH=%PYTHON_DIR%;%PATH%
if not defined PYTHON (set PYTHON=python)

%PYTHON% main.py

pause
