import random
import string
from datetime import datetime
from database import get_db_connection

def generate_room_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def create_room(host_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        code = generate_room_code()
        while True:
            cursor.execute('SELECT id FROM rooms WHERE code = ?', (code,))
            if not cursor.fetchone():
                break
            code = generate_room_code()
        
        cursor.execute(
            'INSERT INTO rooms (code, host_name, status) VALUES (?, ?, ?)',
            (code, host_name, 'waiting')
        )
        room_id = cursor.lastrowid
        
        cursor.execute(
            'INSERT INTO players (room_id, name, is_host) VALUES (?, ?, 1)',
            (room_id, host_name)
        )
        
        conn.commit()
        return code, room_id

def get_room_by_code(code):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rooms WHERE code = ?', (code,))
        row = cursor.fetchone()
        return dict(row) if row else None

def join_room(code, player_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM rooms WHERE code = ?', (code,))
        room = cursor.fetchone()
        if not room:
            return None, "Sala não encontrada"
        
        room_id = room['id']
        
        cursor.execute(
            'SELECT id FROM players WHERE room_id = ? AND name = ?',
            (room_id, player_name)
        )
        if cursor.fetchone():
            return None, "Nome já está em uso nesta sala"
        
        cursor.execute(
            'INSERT INTO players (room_id, name, is_host) VALUES (?, ?, 0)',
            (room_id, player_name)
        )
        conn.commit()
        return room_id, None

def get_players_in_room(room_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM players WHERE room_id = ? ORDER BY is_host DESC, joined_at',
            (room_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_theme_categories():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM theme_categories ORDER BY name')
        return [dict(row) for row in cursor.fetchall()]

def get_themes_by_category(category_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM themes WHERE category_id = ?',
            (category_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def get_random_theme_from_category(category_id):
    themes = get_themes_by_category(category_id)
    if not themes:
        return None
    return random.choice(themes)

def start_round(room_id, category_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        theme = get_random_theme_from_category(category_id)
        if not theme:
            return None, "Nenhum tema disponível nesta categoria"
        
        cursor.execute(
            'INSERT INTO rounds (room_id, theme_id, category_id, status) VALUES (?, ?, ?, ?)',
            (room_id, theme['id'], category_id, 'answering')
        )
        round_id = cursor.lastrowid
        
        players = get_players_in_room(room_id)
        
        used_numbers = set()
        for player in players:
            while True:
                secret_number = random.randint(1, 100)
                if secret_number not in used_numbers:
                    used_numbers.add(secret_number)
                    break
            
            cursor.execute(
                'INSERT INTO player_answers (round_id, player_id, secret_number) VALUES (?, ?, ?)',
                (round_id, player['id'], secret_number)
            )
        
        cursor.execute(
            'UPDATE rooms SET status = ? WHERE id = ?',
            ('playing', room_id)
        )
        
        conn.commit()
        return round_id, None

def get_current_round(room_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT r.*, t.name as theme_name, tc.name as category_name
               FROM rounds r
               JOIN themes t ON r.theme_id = t.id
               JOIN theme_categories tc ON r.category_id = tc.id
               WHERE r.room_id = ?
               ORDER BY r.started_at DESC
               LIMIT 1''',
            (room_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_player_answer(round_id, player_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM player_answers WHERE round_id = ? AND player_id = ?',
            (round_id, player_id)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def submit_answer(round_id, player_id, answer):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE player_answers 
               SET answer = ?, confirmed = 1, answered_at = CURRENT_TIMESTAMP
               WHERE round_id = ? AND player_id = ?''',
            (answer, round_id, player_id)
        )
        conn.commit()

def get_all_answers_for_round(round_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT pa.*, p.name as player_name
               FROM player_answers pa
               JOIN players p ON pa.player_id = p.id
               WHERE pa.round_id = ?
               ORDER BY pa.secret_number''',
            (round_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

def check_all_confirmed(round_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT COUNT(*) as total FROM player_answers WHERE round_id = ?',
            (round_id,)
        )
        total = cursor.fetchone()['total']
        
        cursor.execute(
            'SELECT COUNT(*) as confirmed FROM player_answers WHERE round_id = ? AND confirmed = 1',
            (round_id,)
        )
        confirmed = cursor.fetchone()['confirmed']
        
        return total > 0 and total == confirmed

def transition_to_revealing(round_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE rounds SET status = ? WHERE id = ?',
            ('revealing', round_id)
        )
        
        answers = get_all_answers_for_round(round_id)
        for idx, answer in enumerate(answers):
            cursor.execute(
                'UPDATE player_answers SET reveal_order = ? WHERE id = ?',
                (idx + 1, answer['id'])
            )
        
        conn.commit()

def reveal_next_answer(round_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''SELECT * FROM player_answers 
               WHERE round_id = ? AND revealed = 0
               ORDER BY secret_number
               LIMIT 1''',
            (round_id,)
        )
        answer = cursor.fetchone()
        if answer:
            cursor.execute(
                'UPDATE player_answers SET revealed = 1 WHERE id = ?',
                (answer['id'],)
            )
            conn.commit()
            return True
        return False

def end_round(round_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute('SELECT started_at FROM rounds WHERE id = ?', (round_id,))
        round_data = cursor.fetchone()
        if round_data:
            started_at = datetime.fromisoformat(round_data['started_at'])
            ended_at = datetime.now()
            duration = int((ended_at - started_at).total_seconds())
            
            cursor.execute(
                '''UPDATE rounds 
                   SET status = ?, ended_at = ?, duration_seconds = ?
                   WHERE id = ?''',
                ('completed', ended_at.isoformat(), duration, round_id)
            )
            conn.commit()

def reset_room_for_new_round(room_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE rooms SET status = ? WHERE id = ?',
            ('waiting', room_id)
        )
        conn.commit()

def get_player_by_name_and_room(room_id, player_name):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM players WHERE room_id = ? AND name = ?',
            (room_id, player_name)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

def get_round_history(room_id=None, limit=50):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if room_id:
            cursor.execute(
                '''SELECT r.*, t.name as theme_name, tc.name as category_name, rm.code as room_code
                   FROM rounds r
                   JOIN themes t ON r.theme_id = t.id
                   JOIN theme_categories tc ON r.category_id = tc.id
                   JOIN rooms rm ON r.room_id = rm.id
                   WHERE r.room_id = ?
                   ORDER BY r.started_at DESC
                   LIMIT ?''',
                (room_id, limit)
            )
        else:
            cursor.execute(
                '''SELECT r.*, t.name as theme_name, tc.name as category_name, rm.code as room_code
                   FROM rounds r
                   JOIN themes t ON r.theme_id = t.id
                   JOIN theme_categories tc ON r.category_id = tc.id
                   JOIN rooms rm ON r.room_id = rm.id
                   ORDER BY r.started_at DESC
                   LIMIT ?''',
                (limit,)
            )
        return [dict(row) for row in cursor.fetchall()]
