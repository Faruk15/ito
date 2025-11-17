from database import get_db_connection, init_database

def seed_initial_data():
    init_database()
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM theme_categories')
        if cursor.fetchone()['count'] > 0:
            print("Dados já existem no banco. Pulando seed.")
            return
        
        categories_and_themes = {
            "Esportes": [
                "Jogadores de futebol mais famosos",
                "Times de futebol brasileiros (tamanho do clube)",
                "Esportes radicais",
                "Atletas brasileiros mais respeitados",
                "Maiores premiações esportivas",
                "Jogadores de futebol mais bem pagos",
                "Jogadores de futebol mais plásticos",
                "Jogadores de futebol mais rápidos",
            ],
            "Filmes": [
                "Filmes de ação com mais aura",
                "Filmes de comédia mais engraçados",
                "Melhores filmes da Disney/Pixar",
                "Filmes de terror que dão mais medo",
                "Melhores filmes brasileiros",
            ],
            "Comidas": [
                "Frutas mais consumidas no Brasil",
                "Frutas mais gostosas",
                "Pratos brasileiros",
                "Doces e sobremesas",
                "Fast food mais gostoso (empresa)",
                "",
            ],
            "Música": [
                "Cantores gringos mais famosos",
                "Cantores brasileiros mais famosos",
                "Instrumentos musicais mais populares",
            ],
            "Famosos": [
                "Atores de Hollywood",
                "Apresentadores de TV brasileiros",
                "Youtubers mais relevantes na internet",
                "Cantores internacionais",
                "Jogadores de futebol",
            ],
            "Animais": [
                "Animais domésticos mais fofos",
                "Animais selvagens que você conseguiria sair na mão",
                "Animais marinhos mais perigosos",
                "Aves mais fodas",
                "Insetos mais insuportáveis",
            ],
            "Lugares": [
                "Países mais ricos",
                "Cidades brasileiras",
                "Pontos turísticos mais visitados",
                "Capitais do mundo mais sujas",
            ],
            "Profissões": [
                "Profissões da saúde",
                "Profissões criativas",
                "Profissões técnicas",
                "Profissões antigas",
                "Profissões do futuro",
            ],
            "Jogos": [
                "Jogos de cartas famosos",
                "Melhores jogos antigos",
                "Jogos de RPG mais populares",
                "Jogos de luta mais populares",
                "Jogos de corrida mais populares",
                "Jogos de plataforma mais populares",
                "Jogos multiplayer online",
                "Jogos mobile mais populares",
                "Personagens de jogos famosos",
                "Franquias de jogos famosas",
                "Melhores consoles",
                "Jogos de estratégia",
                "Jogos de terror que mais dão medo",
                "Jogos party game mais divertidos",
            ],
        }
        
        for category_name, themes in categories_and_themes.items():
            cursor.execute(
                'INSERT INTO theme_categories (name) VALUES (?)',
                (category_name,)
            )
            category_id = cursor.lastrowid
            
            for theme_name in themes:
                cursor.execute(
                    'INSERT INTO themes (category_id, name) VALUES (?, ?)',
                    (category_id, theme_name)
                )
        
        conn.commit()
        print("Dados iniciais inseridos com sucesso!")
        print(f"Categorias criadas: {len(categories_and_themes)}")
        print(f"Temas criados: {sum(len(themes) for themes in categories_and_themes.values())}")

if __name__ == '__main__':
    seed_initial_data()
