@REM Jellytion
@REM The MIT License (MIT)
@REM Copyright (c) 2025 Jonathan Chiu

@echo off

cd /d %~dp0
cd ..

pip3 install -r requirements.txt

python3 main.py
