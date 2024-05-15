@echo off

set DIR=%~dp0
set PYTHON_DIR=%DIR%\python

set PATH=%DIR%\git\bin;%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%
set PY_LIBS=%PYTHON_DIR%\Scripts\Lib;%PYTHON_DIR%\Scripts\Lib\site-packages
set PY_PIP=%PYTHON_DIR%\Scripts
set SKIP_VENV=1
set PIP_INSTALLER_LOCATION=%PYTHON_DIR%\get-pip.py

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=
