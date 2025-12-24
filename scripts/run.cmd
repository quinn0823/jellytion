@REM Jellytion
@REM The MIT License (MIT)
@REM Copyright (c) 2025 Jonathan Chiu

@echo off

cd /d %~dp0
cd ..

pip install -r requirements.txt

python main.py
