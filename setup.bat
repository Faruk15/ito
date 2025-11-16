@echo off
echo Configurando o Jogo Ito...

if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt

echo Inicializando banco de dados...
python seed_data.py

echo.
echo Configuracao completa!
echo.
echo Para executar o jogo, use:
echo   run.bat
echo.
echo Ou manualmente:
echo   venv\Scripts\activate.bat
echo   streamlit run app.py

pause
