# 🎮 Jogo Ito - Aplicação Web

Uma aplicação web completa do jogo Ito, desenvolvida com Python e Streamlit, permitindo que você jogue com seus amigos online!

## 📋 Sobre o Jogo

O Ito é um jogo cooperativo onde cada jogador recebe um número secreto (de 1 a 100) e deve escolher uma resposta relacionada ao tema sorteado que represente a magnitude do seu número. O objetivo é revelar as respostas em ordem crescente dos números secretos.

## 🚀 Como Executar

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes do Python)

### Instalação

1. Clone ou baixe este projeto

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

4. Abra seu navegador em `http://localhost:8501`

## 🎯 Como Jogar

### 1. Criar uma Sala

- Na tela inicial, digite seu nome e clique em "Criar Sala"
- Você receberá um código de sala (ex: ABC123)
- Compartilhe este código com seus amigos

### 2. Entrar em uma Sala

- Digite o código da sala e seu nome
- Clique em "Entrar"

### 3. Iniciar uma Rodada

- O host escolhe uma categoria de tema
- Clica em "Iniciar Rodada"
- Cada jogador recebe um número secreto

### 4. Fase de Resposta

- Veja seu número secreto e o tema sorteado
- Digite uma resposta que represente a magnitude do seu número
- Clique em "Confirmar Resposta"
- Aguarde todos os jogadores confirmarem

### 5. Fase de Revelação

- As respostas aparecem em ordem crescente, mas ocultas
- O host clica em "Revelar Próximo" para mostrar cada resposta
- Descubra se as respostas estão na ordem correta!

### 6. Finalizar

- Após revelar todas as respostas, o host pode:
  - Iniciar uma nova rodada
  - Encerrar a partida

## 📊 Histórico de Partidas

- Na tela inicial, clique em "Ver Histórico de Partidas"
- Veja todas as rodadas jogadas, com:
  - Sala, categoria e tema
  - Data e hora
  - Duração da rodada
  - Todas as respostas e números secretos

## 🗄️ Banco de Dados

### Estrutura

O projeto usa SQLite com as seguintes tabelas:

- **theme_categories**: Categorias de temas (Esportes, Filmes, etc.)
- **themes**: Temas específicos dentro de cada categoria
- **rooms**: Salas de jogo
- **players**: Jogadores em cada sala
- **rounds**: Rodadas jogadas
- **player_answers**: Respostas de cada jogador em cada rodada

### Adicionar Novos Temas

Você pode adicionar temas diretamente no banco de dados:

1. **Via Python:**
```python
from database import get_db_connection

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # Adicionar nova categoria
    cursor.execute("INSERT INTO theme_categories (name) VALUES (?)", ("Nova Categoria",))
    category_id = cursor.lastrowid
    
    # Adicionar temas nessa categoria
    cursor.execute("INSERT INTO themes (category_id, name) VALUES (?, ?)", 
                   (category_id, "Tema Específico 1"))
    cursor.execute("INSERT INTO themes (category_id, name) VALUES (?, ?)", 
                   (category_id, "Tema Específico 2"))
    
    conn.commit()
```

2. **Via SQLite CLI:**
```bash
sqlite3 ito_game.db
```
```sql
-- Ver categorias existentes
SELECT * FROM theme_categories;

-- Adicionar nova categoria
INSERT INTO theme_categories (name) VALUES ('Tecnologia');

-- Adicionar temas (substitua 9 pelo ID da categoria)
INSERT INTO themes (category_id, name) VALUES (9, 'Linguagens de programação');
INSERT INTO themes (category_id, name) VALUES (9, 'Redes sociais');
```

### Consultar Histórico

```python
from models import get_round_history

# Ver últimas 50 rodadas
history = get_round_history(limit=50)

for round_data in history:
    print(f"Sala: {round_data['room_code']}")
    print(f"Tema: {round_data['theme_name']}")
    print(f"Duração: {round_data['duration_seconds']}s")
```

## 📁 Estrutura do Projeto

```
.
├── app.py              # Aplicação principal Streamlit
├── database.py         # Conexão e inicialização do banco
├── models.py           # Funções de acesso aos dados
├── seed_data.py        # Script para popular dados iniciais
├── requirements.txt    # Dependências do projeto
├── README.md          # Este arquivo
└── ito_game.db        # Banco de dados SQLite (criado automaticamente)
```

## 🔧 Configuração

### Mudar o Caminho do Banco de Dados

Por padrão, o banco é criado como `ito_game.db` no diretório atual. Para mudar:

```bash
export DB_PATH=/caminho/para/seu/banco.db
streamlit run app.py
```

### Popular Dados Iniciais Manualmente

Se precisar repopular os temas:

```bash
python seed_data.py
```

## 🎨 Categorias e Temas Inclusos

O projeto já vem com 8 categorias e 40 temas:

- **Esportes**: Jogadores de futebol, modalidades olímpicas, times, etc.
- **Filmes**: Ação, comédia, Disney/Pixar, terror, brasileiros
- **Comidas**: Frutas, pratos brasileiros, doces, fast food, japonesas
- **Música**: Bandas de rock, cantores, estilos, instrumentos
- **Famosos**: Atores, apresentadores, youtubers, cantores
- **Animais**: Domésticos, selvagens, marinhos, aves, insetos
- **Lugares**: Países, cidades, pontos turísticos, praias, capitais
- **Profissões**: Saúde, criativas, técnicas, antigas, do futuro

## 🌐 Deploy

### Streamlit Cloud (Gratuito)

1. Faça upload do projeto no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte seu repositório
4. Deploy automático!

### Heroku, Railway, Render

Todos suportam Streamlit. Adicione um arquivo `Procfile`:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

## ⚠️ Observações Importantes

- **Sincronização**: A aplicação usa auto-refresh (a cada 2 segundos) para sincronizar os jogadores
- **Sem mínimo de jogadores**: O host pode iniciar rodadas sozinho para testar
- **Banco local**: Por padrão usa SQLite local. Para produção com múltiplos usuários, considere PostgreSQL
- **Estado da sessão**: Cada jogador mantém seu estado no navegador via `st.session_state`

## 🐛 Solução de Problemas

### Erro ao iniciar

```bash
# Reinstale as dependências
pip install --upgrade -r requirements.txt
```

### Banco não inicializa

```bash
# Delete o banco e reinicie
rm ito_game.db
python seed_data.py
streamlit run app.py
```

### Jogadores não sincronizam

- Certifique-se de que todos estão na mesma sala (mesmo código)
- Aguarde alguns segundos para o auto-refresh
- Recarregue a página (F5)

## 📝 Licença

Projeto livre para uso pessoal e educacional.

## 🤝 Contribuições

Sinta-se à vontade para adicionar novos temas, melhorar a interface ou adicionar funcionalidades!

---

**Divirta-se jogando Ito! 🎉**
