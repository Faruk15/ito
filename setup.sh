#!/bin/bash

echo "🎮 Configurando o Jogo Ito..."

if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
fi

echo "Ativando ambiente virtual..."
. venv/bin/activate

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Inicializando banco de dados..."
python seed_data.py

echo ""
echo "✅ Configuração completa!"
echo ""
echo "Para executar o jogo, use:"
echo "  ./run.sh"
echo ""
echo "Ou manualmente:"
echo "  . venv/bin/activate"
echo "  streamlit run app.py"
