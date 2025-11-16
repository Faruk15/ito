import streamlit as st
import time
from datetime import datetime
from database import init_database
from seed_data import seed_initial_data
import models

st.set_page_config(
    page_title="Ito",
    page_icon="🎮",
    layout="wide"
)

init_database()
seed_initial_data()

if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'room_code' not in st.session_state:
    st.session_state.room_code = None
if 'player_name' not in st.session_state:
    st.session_state.player_name = None
if 'room_id' not in st.session_state:
    st.session_state.room_id = None
if 'is_host' not in st.session_state:
    st.session_state.is_host = False
if 'round_start_time' not in st.session_state:
    st.session_state.round_start_time = None

def go_to_home():
    st.session_state.page = 'home'
    st.session_state.room_code = None
    st.session_state.player_name = None
    st.session_state.room_id = None
    st.session_state.is_host = False
    st.session_state.round_start_time = None
    st.rerun()

def show_home_page():
    st.title("Ito")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Criar Nova Sala")
        host_name = st.text_input("Seu nome:", key="host_name_input")
        if st.button("Criar Sala", type="primary", use_container_width=True):
            if host_name.strip():
                code, room_id = models.create_room(host_name.strip())
                st.session_state.room_code = code
                st.session_state.player_name = host_name.strip()
                st.session_state.room_id = room_id
                st.session_state.is_host = True
                st.session_state.page = 'room'
                st.rerun()
            else:
                st.error("Por favor, digite seu nome")
    
    with col2:
        st.subheader("Entrar em uma Sala")
        join_code = st.text_input("Código da sala:", key="join_code_input")
        join_name = st.text_input("Seu nome:", key="join_name_input")
        if st.button("Entrar", type="primary", use_container_width=True):
            if join_code.strip() and join_name.strip():
                room_id, error = models.join_room(join_code.strip().upper(), join_name.strip())
                if error:
                    st.error(error)
                else:
                    st.session_state.room_code = join_code.strip().upper()
                    st.session_state.player_name = join_name.strip()
                    st.session_state.room_id = room_id
                    st.session_state.is_host = False
                    st.session_state.page = 'room'
                    st.rerun()
            else:
                st.error("Por favor, preencha todos os campos")
    
    st.markdown("---")
    if st.button("📊 Ver Histórico de Partidas"):
        st.session_state.page = 'history'
        st.rerun()

def format_duration(seconds):
    if seconds is None:
        return "N/A"
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}m {secs}s"

def show_history_page():
    st.title("📊 Histórico de Partidas")
    
    if st.button("← Voltar"):
        go_to_home()
    
    st.markdown("---")
    
    history = models.get_round_history(limit=100)
    
    if not history:
        st.info("Nenhuma partida jogada ainda.")
        return
    
    for round_data in history:
        with st.expander(
            f"🎯 Sala {round_data['room_code']} - {round_data['category_name']} - "
            f"{datetime.fromisoformat(round_data['started_at']).strftime('%d/%m/%Y %H:%M')}"
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Tema:** {round_data['theme_name']}")
            with col2:
                st.write(f"**Status:** {round_data['status']}")
            with col3:
                st.write(f"**Duração:** {format_duration(round_data['duration_seconds'])}")
            
            answers = models.get_all_answers_for_round(round_data['id'])
            if answers:
                st.write("**Respostas:**")
                for ans in answers:
                    st.write(f"- {ans['player_name']}: {ans['answer']} (Número: {ans['secret_number']})")

def show_room_page():
    room = models.get_room_by_code(st.session_state.room_code)
    if not room:
        st.error("Sala não encontrada")
        go_to_home()
        return
    
    current_round = models.get_current_round(st.session_state.room_id)
    
    if current_round and current_round['status'] in ['answering', 'revealing']:
        if current_round['status'] == 'answering':
            show_answering_phase(current_round)
        else:
            show_revealing_phase(current_round)
    else:
        show_waiting_room(room)

def show_waiting_room(room):
    st.title(f"🎮 Sala: {st.session_state.room_code}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Host: {room['host_name']}")
    with col2:
        if st.button("🚪 Sair da Sala"):
            go_to_home()
    
    st.markdown("---")
    
    players = models.get_players_in_room(st.session_state.room_id)
    
    st.subheader(f"👥 Jogadores ({len(players)})")
    for player in players:
        icon = "👑" if player['is_host'] else "👤"
        st.write(f"{icon} {player['name']}")
    
    st.markdown("---")
    
    if st.session_state.is_host:
        st.subheader("🎯 Iniciar Rodada")
        
        categories = models.get_theme_categories()
        if categories:
            category_names = [cat['name'] for cat in categories]
            selected_category = st.selectbox("Escolha uma categoria:", category_names)
            
            if st.button("🚀 Iniciar Rodada", type="primary", use_container_width=True):
                category_id = next(cat['id'] for cat in categories if cat['name'] == selected_category)
                round_id, error = models.start_round(st.session_state.room_id, category_id)
                if error:
                    st.error(error)
                else:
                    st.session_state.round_start_time = time.time()
                    st.rerun()
        else:
            st.warning("Nenhuma categoria disponível. Execute seed_data.py primeiro.")
    else:
        st.info("Aguardando o host iniciar a rodada...")
    
    time.sleep(2)
    st.rerun()

def show_answering_phase(current_round):
    st.title(f"🎮 Sala: {st.session_state.room_code}")
    
    if st.session_state.round_start_time is None:
        st.session_state.round_start_time = time.time()
    
    elapsed = int(time.time() - st.session_state.round_start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"📝 Tema: {current_round['theme_name']}")
        st.caption(f"Categoria: {current_round['category_name']}")
    with col2:
        st.metric("⏱️ Tempo", f"{minutes:02d}:{seconds:02d}")
    
    st.markdown("---")
    
    player = models.get_player_by_name_and_room(st.session_state.room_id, st.session_state.player_name)
    if not player:
        st.error("Jogador não encontrado")
        return
    
    player_answer = models.get_player_answer(current_round['id'], player['id'])
    if not player_answer:
        st.error("Resposta não encontrada")
        return
    
    st.subheader(f"🔢 Seu número secreto: {player_answer['secret_number']}")
    
    if player_answer['confirmed']:
        st.success(f"✅ Sua resposta foi confirmada: **{player_answer['answer']}**")
        st.info("Aguardando os outros jogadores...")
    else:
        answer_text = st.text_input(
            "Digite sua resposta:",
            key="answer_input",
            placeholder="Ex: Pelé, Pizza, etc."
        )
        
        if st.button("✅ Confirmar Resposta", type="primary"):
            if answer_text.strip():
                models.submit_answer(current_round['id'], player['id'], answer_text.strip())
                st.rerun()
            else:
                st.error("Por favor, digite uma resposta")
    
    st.markdown("---")
    
    all_answers = models.get_all_answers_for_round(current_round['id'])
    confirmed_count = sum(1 for ans in all_answers if ans['confirmed'])
    total_count = len(all_answers)
    
    st.progress(confirmed_count / total_count if total_count > 0 else 0)
    st.write(f"**Progresso:** {confirmed_count}/{total_count} jogadores confirmaram")
    
    for ans in all_answers:
        status = "✅" if ans['confirmed'] else "⏳"
        st.write(f"{status} {ans['player_name']}")
    
    if models.check_all_confirmed(current_round['id']):
        models.transition_to_revealing(current_round['id'])
        st.rerun()
    
    time.sleep(2)
    st.rerun()

def show_revealing_phase(current_round):
    st.title(f"🎮 Sala: {st.session_state.room_code}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"🎯 Revelação: {current_round['theme_name']}")
        st.caption(f"Categoria: {current_round['category_name']}")
    with col2:
        if st.button("🚪 Voltar ao Lobby"):
            models.end_round(current_round['id'])
            models.reset_room_for_new_round(st.session_state.room_id)
            st.session_state.round_start_time = None
            st.rerun()
    
    st.markdown("---")
    
    all_answers = models.get_all_answers_for_round(current_round['id'])
    
    revealed_count = sum(1 for ans in all_answers if ans['revealed'])
    total_count = len(all_answers)
    
    if st.session_state.is_host and revealed_count < total_count:
        if st.button("👁️ Revelar Próximo", type="primary", use_container_width=True):
            models.reveal_next_answer(current_round['id'])
            st.rerun()
    
    st.markdown("---")
    
    for ans in all_answers:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            st.write(f"**#{ans['secret_number']}**")
        with col2:
            if ans['revealed']:
                st.write(f"**{ans['player_name']}:** {ans['answer']}")
            else:
                st.write(f"**{ans['player_name']}:** ████████")
        with col3:
            if ans['revealed']:
                st.write("✅ Revelado")
            else:
                st.write("🔒 Oculto")
    
    if revealed_count == total_count:
        st.success("🎉 Todas as respostas foram reveladas!")
        
        if st.session_state.is_host:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Nova Rodada", type="primary", use_container_width=True):
                    models.end_round(current_round['id'])
                    models.reset_room_for_new_round(st.session_state.room_id)
                    st.session_state.round_start_time = None
                    st.rerun()
            with col2:
                if st.button("🏁 Encerrar Partida", use_container_width=True):
                    models.end_round(current_round['id'])
                    models.reset_room_for_new_round(st.session_state.room_id)
                    go_to_home()
    
    time.sleep(2)
    st.rerun()

if st.session_state.page == 'home':
    show_home_page()
elif st.session_state.page == 'room':
    show_room_page()
elif st.session_state.page == 'history':
    show_history_page()
