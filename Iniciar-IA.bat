@echo off
cd /d "%~dp0"
title IA-Programacao

echo ========================================
echo          IA-Programacao
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo ERRO: ambiente virtual .venv nao encontrado.
    pause
    exit /b 1
)

if not exist "main.py" (
    echo ERRO: main.py nao encontrado.
    pause
    exit /b 1
)

echo Iniciando a IA...
echo.

".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo A IA foi encerrada com erro.
    pause
)
