@echo off
chcp 65001 >nul
echo ===============================================
echo 🔍 SAW IA - Verificador de Fotos Samsung
echo ===============================================

REM Recebe o caminho da pasta clicada
set "PASTA=%~1"

REM Verifica se a pasta foi fornecida
if "%PASTA%"=="" (
    echo ❌ Erro: Nenhuma pasta foi selecionada!
    pause
    exit /b 1
)

echo 📁 Pasta selecionada: %PASTA%

REM Verifica se a pasta existe
if not exist "%PASTA%" (
    echo ❌ Erro: A pasta não existe!
    pause
    exit /b 1
)

REM Caminho para o projeto (AJUSTE CONFORME SUA INSTALAÇÃO)
set "PROJETO_DIR=C:\Users\Usuário\Documents\saw_IA"
set "VENV_PATH=%PROJETO_DIR%\venv\Scripts\activate.bat"
set "SCRIPT_PATH=%PROJETO_DIR%\src\verificar.py"

REM Verifica se o ambiente virtual existe
if not exist "%VENV_PATH%" (
    echo ❌ Erro: Ambiente virtual não encontrado em:
    echo    %VENV_PATH%
    echo.
    echo 💡 Certifique-se de que o projeto está instalado corretamente.
    pause
    exit /b 1
)

REM Verifica se o script existe
if not exist "%SCRIPT_PATH%" (
    echo ❌ Erro: Script verificar.py não encontrado em:
    echo    %SCRIPT_PATH%
    pause
    exit /b 1
)

echo 🔄 Ativando ambiente virtual...
call "%VENV_PATH%"

if errorlevel 1 (
    echo ❌ Erro ao ativar o ambiente virtual!
    pause
    exit /b 1
)

echo 🚀 Executando verificação...
echo.

REM Executa o script Python
python "%SCRIPT_PATH%" "%PASTA%"

REM Verifica se houve erro na execução
if errorlevel 1 (
    echo.
    echo ❌ Erro durante a execução do script!
) else (
    echo.
    echo ✅ Verificação concluída!
)

echo.
echo ===============================================
echo Pressione qualquer tecla para fechar...
pause >nul