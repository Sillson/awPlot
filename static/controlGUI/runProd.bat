@echo off
call :GET_THIS_DIR
chdir %THIS_DIR%
call activate awdb
python runProd.py
call deactivate

:GET_THIS_DIR
pushd %~dp0
set THIS_DIR=%CD%
popd
