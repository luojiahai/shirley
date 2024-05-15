@echo off

set DIR=%~dp0

set PATH=%DIR%\git\bin;%DIR%\python;%DIR%\python\Scripts;%PATH%
set PY_LIBS=%DIR%\python\Scripts\Lib;%DIR%\python\Scripts\Lib\site-packages
set PY_PIP=%DIR%\python\Scripts
set SKIP_VENV=1
set PIP_INSTALLER_LOCATION=%DIR%\python\get-pip.py

set PYTHON=
set GIT=
set VENV_DIR=
set COMMANDLINE_ARGS=
