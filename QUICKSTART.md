# 🚀 Início Rápido - Jogo Ito

## Instalação e Execução (3 passos)

### Linux/Mac:
```bash
# 1. Execute o setup (apenas na primeira vez)
./setup.sh

# 2. Execute o jogo
./run.sh
```

### Windows:
```cmd
# 1. Execute o setup (apenas na primeira vez)
setup.bat

# 2. Execute o jogo
run.bat
```

### Manual (qualquer sistema):
```bash
# 1. Crie o ambiente virtual
python3 -m venv venv

# 2. Ative o ambiente virtual
# Linux/Mac:
. venv/bin/activate
# Windows:
venv\Scripts\activate.bat

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o jogo
streamlit run app.py
```

## Como Jogar (resumo)

1. **Criar Sala**: Digite seu nome → "Criar Sala" → Compartilhe o código
2. **Entrar**: Digite código + nome → "Entrar"
3. **Jogar**: Host escolhe categoria → Todos respondem → Host revela
4. **Repetir**: Nova rodada ou encerrar

## Estrutura do Projeto

```
.
├── app.py              # 🎮 Aplicação principal
├── database.py         # 💾 Banco de dados
├── models.py           # 📊 Lógica de dados
├── seed_data.py        # 🌱 Dados iniciais
├── requirements.txt    # 📦 Dependências
├── setup.sh / .bat     # ⚙️ Instalação
├── run.sh / .bat       # ▶️ Execução
└── README.md           # 📖 Documentação completa
```

## Adicionar Novos Temas

Edite `seed_data.py` e adicione na estrutura `categories_and_themes`:

```python
"Nova Categoria": [
    "Tema 1",
    "Tema 2",
    "Tema 3",
],
```

Depois delete o banco e execute novamente:
```bash
rm ito_game.db
python seed_data.py
```

## Problemas Comuns

**Erro ao instalar**: Certifique-se de ter Python 3.8+ instalado
```bash
python3 --version
```

**Porta ocupada**: Streamlit usa porta 8501 por padrão. Para mudar:
```bash
streamlit run app.py --server.port 8502
```

**Banco corrompido**: Delete e recrie
```bash
rm ito_game.db
python seed_data.py
```

## Acesso Remoto

Para jogar com amigos em rede local:
```bash
streamlit run app.py --server.address 0.0.0.0
```

Compartilhe seu IP local (ex: 192.168.1.100:8501)

## Deploy Online (Grátis)

1. Crie conta no [Streamlit Cloud](https://share.streamlit.io)
2. Conecte seu repositório GitHub
3. Deploy automático!

---

**Dúvidas?** Veja o [README.md](README.md) completo
