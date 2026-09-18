import streamlit as st
import time
import base64
import os
import psycopg2

st.set_page_config(
    page_title="WELCOME! Quiz da Lorylland 🎮",
    page_icon="🕹️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONEXÃO COM POSTGRESQL (RENDER) ---
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_connection():
    if not DATABASE_URL:
        st.error("Erro: Variável de ambiente DATABASE_URL não encontrada no Render.")
        st.stop()
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS ranking (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            heroi TEXT NOT NULL
        )
    ''')
    conn.commit()
    c.close()
    conn.close()

def save_score(nome, pontos, heroi):
    conn = get_connection()
    c = conn.cursor()
    c.execute('INSERT INTO ranking (nome, pontos, heroi) VALUES (%s, %s, %s)', (nome, pontos, heroi))
    conn.commit()
    c.close()
    conn.close()

def get_top_ranking(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT nome, pontos, heroi FROM ranking ORDER BY pontos DESC, id ASC LIMIT %s', (limit,))
    rows = c.fetchall()
    c.close()
    conn.close()
    return rows

init_db()

def load_asset_b64(possible_names, default_url=""):
    if isinstance(possible_names, str):
        possible_names = [possible_names]
    for name in possible_names:
        for ext in ["png", "gif", "jpg", "jpeg", "webp", "PNG", "GIF", "JPG"]:
            file_path = f"{name}.{ext}"
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                    mime_ext = ext.lower()
                    mime = "jpeg" if mime_ext in ["jpg", "jpeg"] else mime_ext
                    return f"data:image/{mime};base64,{encoded}"
    return default_url

def load_audio_b64():
    audio_files = ["arcade.mp3", "arcade.MP3", "musica.mp3", "som_arcade.mp3", "arcade.wav", "arcade.WAV"]
    for file in audio_files:
        if os.path.exists(file):
            with open(file, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
                ext = file.split(".")[-1].lower()
                return f"data:audio/{ext};base64,{encoded}"
    return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

audio_src = load_audio_b64()

# 1. IMAGENS DE FUNDO
bg_entrada = load_asset_b64(["entrada", "bg_entrada"],
                            "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=1200")
bg_gif = load_asset_b64(["fundo", "fundo_gif", "fundo_8bit"], bg_entrada)

# 2. AVATAR DE LORYLLAND
lory_img = load_asset_b64(["lorylland", "lory", "kaila", "kayla", "avatar"],
                          "https://cdn-icons-png.flaticon.com/512/4140/4140048.png")

# 3. ASSETS HOMEM-ARANHA
spidey_main = load_asset_b64(["homemaranha", "spidey"],
                             "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Spider-Man.jpg/800px-Spider-Man.jpg")
spidey_fall = load_asset_b64(["homemaranha_caindo", "spidey_caindo"], spidey_main)
spidey_web = load_asset_b64(["teia", "homemaranha_teia", "spidey_teia"], spidey_main)

# 4. ASSETS HOMEM DE FERRO
ironman_main = load_asset_b64(["Homem de Ferro", "homemdeferro", "ironman"],
                              "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Iron_Man_cosplay.jpg/800px-Iron_Man_cosplay.jpg")
ironman_fall = load_asset_b64(["homemdeferro_caindo", "ironman_caindo"], ironman_main)
ironman_fire = load_asset_b64(["fogo", "homemdeferro_fogo", "ironman_fogo"], ironman_main)

# BANCO COM AS 20 PERGUNTAS
perguntas = [
    {"q": "1. Qual sua fruta favorita?", "opts": ["Laranja", "Morango", "Banana"], "ans": ["Morango"]},
    {"q": "2. Quem é sua pessoa favorita?", "opts": ["Harry Styles", "Eva", "Patrick Jane"], "ans": ["Eva"]},
    {"q": "3. Quantos livros ela já leu este ano?", "opts": ["12", "27", "16"], "ans": ["16"]},
    {"q": "4. Qual sua cor favorita?", "opts": ["Roxo", "Amarelo", "Vermelho"], "ans": ["Vermelho"]},
    {"q": "5. Qual foi o primeiro livro que ela leu?",
     "opts": ["O Ratinho do Campo e o Ratinho da Cidade", "Alice no País das Maravilhas",
              "As Princesas Também Soltam Pum"], "ans": ["Alice no País das Maravilhas"]},
    {"q": "6. Quantos países ela já visitou?", "opts": ["6", "8", "9"], "ans": ["6"]},
    {"q": "7. Qual seu filme favorito?",
     "opts": ["It: A Coisa", "Alice no País das Maravilhas", "Castle in the Sky", "Todos servem"],
     "ans": ["It: A Coisa", "Alice no País das Maravilhas", "Castle in the Sky"]},
    {"q": "8. O que lhe traz mais alegria?", "opts": ["Estudar as escrituras", "Cozinhar", "Comer com os amigos"],
     "ans": ["Comer com os amigos"]},
    {"q": "9. Qual a data de seu aniversário?", "opts": ["03/04/2006", "10/08/2006", "02/06/2006"],
     "ans": ["02/06/2006"]},
    {"q": "10. Qual seu cantor favorito?", "opts": ["Niall Horan", "Taylor Swift", "Olívia Rodrigo"],
     "ans": ["Olívia Rodrigo"]},
    {"q": "11. Quantos anos ela tinha quando aprendeu a ler?", "opts": ["5", "8", "3"], "ans": ["5"]},
    {"q": "12. Qual o nome de seu restaurante favorito?", "opts": ["Outback", "Kotay", "Monster Burguer"],
     "ans": ["Monster Burguer"]},
    {"q": "13. Quais línguas ela fala?",
     "opts": ["Inglês, português e francês", "Inglês e português", "Inglês, português e espanhol"],
     "ans": ["Inglês e português"]},
    {"q": "14. Qual seu gênero literário favorito?", "opts": ["Romance", "Suspense", "Fantasia"], "ans": ["Suspense"]},
    {"q": "15. O que ela mais gosta de fazer?", "opts": ["Ler", "Assistir série", "Montar Lego"], "ans": ["Ler"]},
    {"q": "16. Qual é a série de TV favorita da Lorylland?", "opts": ["Anne With an E", "Psych", "Mentalista"],
     "ans": ["Psych"]},
    {"q": "17. Qual suco ela sempre pede quando sai para comer?", "opts": ["Morango", "Maracujá", "Laranja"],
     "ans": ["Laranja"]},
    {"q": "18. Até que série ela foi para a escola?", "opts": ["Nunca foi", "1º ano do ensino médio", "8º ano"],
     "ans": ["8º ano"]},
    {"q": "19. Quantos livros ela leu nos últimos 5 anos?", "opts": ["304", "200", "157"], "ans": ["304"]},
    {"q": "20. Qual seu livro favorito?",
     "opts": ["Enquanto Houver Limoeiros", "Uma Vida Pequena", "Um Homem Chamado Ove"],
     "ans": ["Enquanto Houver Limoeiros"]}
]

# ESTADOS DO JOGO
if 'state' not in st.session_state:
    st.session_state.state = 'welcome'
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'fighter' not in st.session_state:
    st.session_state.fighter = None
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'last_action' not in st.session_state:
    st.session_state.last_action = None
if 'score_saved' not in st.session_state:
    st.session_state.score_saved = False

# TROCA O FUNDO
current_bg = bg_entrada if st.session_state.state == 'welcome' else bg_gif

# CONTROLO DE ÁUDIO NO TOPO DA PÁGINA
st.markdown(f'''
    <div style="text-align: center; margin-bottom: 10px;">
        <span style="font-size: 0.7rem; color: #f8d800;">🔊 MÚSICA DE FUNDO (Clique em PLAY se não tocar sozinho):</span><br>
        <audio controls autoplay loop style="height: 30px; margin-top: 5px;">
            <source src="{audio_src}" type="audio/mp3">
            O seu navegador não suporta o elemento de áudio.
        </audio>
    </div>
''', unsafe_allow_html=True)

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    header, footer {{ visibility: hidden !important; }}

    .stApp, [data-testid="stAppViewContainer"] {{
        background: url("{current_bg}") no-repeat center center fixed !important;
        background-size: cover !important;
        width: 100vw !important;
        min-height: 100vh !important;
        font-family: 'Press Start 2P', monospace !important;
        color: #ffffff;
    }}

    .lory-avatar-large {{
        width: 230px;
        height: 230px;
        border-radius: 50%;
        border: 6px solid #f8d800;
        box-shadow: 0 0 35px #f8d800, 0 0 15px #000;
        object-fit: cover;
        margin: 10px auto 15px auto;
        display: block;
        animation: pulseAvatar 1.5s infinite alternate;
    }}

    @keyframes pulseAvatar {{
        0% {{ transform: scale(1); box-shadow: 0 0 25px #f8d800; }}
        100% {{ transform: scale(1.05); box-shadow: 0 0 45px #e60012; }}
    }}

    .arcade-card {{
        background: rgba(10, 5, 20, 0.92);
        border: 4px solid #f8d800;
        border-radius: 15px;
        box-shadow: 0 0 0 4px #000, 8px 8px 0px rgba(0,0,0,0.8);
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }}

    .hero-container-full {{
        background: rgba(0, 0, 0, 0.92);
        border: 4px solid #f8d800;
        border-radius: 15px;
        box-shadow: 0 0 0 4px #000, 8px 8px 0px rgba(0,0,0,0.8);
        height: 380px;
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        position: relative;
        padding: 10px;
    }}

    .hero-img-full {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        border-radius: 10px;
    }}

    .question-card {{
        background: rgba(0, 0, 0, 0.92);
        border: 4px solid #0078f8;
        border-radius: 12px;
        box-shadow: 0 0 0 4px #000;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }}

    .web-overlay-effect {{
        background: radial-gradient(circle, rgba(255,255,255,0.4) 0%, rgba(0,20,50,0.92) 85%);
        border: 5px dashed #ffffff;
        box-shadow: 0 0 35px #ffffff, inset 0 0 25px #0088ff;
    }}

    .fire-overlay-effect {{
        background: radial-gradient(circle, rgba(255, 100, 0, 0.5) 0%, rgba(30, 0, 0, 0.95) 85%);
        border: 5px solid #ff4500;
        box-shadow: 0 0 40px #ff4500, inset 0 0 30px #ffd700;
    }}

    .fall-anim {{
        animation: fallDown 1.2s cubic-bezier(0.55, 0.085, 0.68, 0.53) forwards;
        width: 100%;
        height: 100%;
        object-fit: contain;
    }}

    @keyframes fallDown {{
        0% {{ transform: translateY(-130px) rotate(0deg); opacity: 1; }}
        50% {{ transform: translateY(70px) rotate(45deg); opacity: 0.85; }}
        100% {{ transform: translateY(280px) rotate(180deg); opacity: 0; }}
    }}

    .blink-text {{
        animation: blink 0.5s steps(2, start) infinite;
        color: #f8d800;
        text-shadow: 3px 3px 0px #e60012;
    }}

    @keyframes blink {{ 50% {{ opacity: 0; }} }}

    .stTextInput input {{
        background-color: #000000 !important;
        color: #f8d800 !important;
        font-family: 'Press Start 2P', monospace !important;
        border: 3px solid #f8d800 !important;
        border-radius: 8px !important;
        text-align: center !important;
        padding: 12px !important;
        font-size: 0.9rem !important;
    }}

    .stButton>button {{
        width: 100% !important;
        background-color: #e60012 !important;
        color: #ffffff !important;
        font-family: 'Press Start 2P', monospace !important;
        font-size: 0.85rem !important;
        padding: 18px !important;
        border: 3px solid #ffffff !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 0 0 #800000, 4px 4px 0px #000 !important;
        margin-top: 10px !important;
    }}

    .stButton>button:hover {{
        background-color: #f8d800 !important;
        color: #000000 !important;
    }}

    .ranking-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        font-size: 0.75rem;
    }}
    .ranking-table th {{
        background-color: #e60012;
        color: #ffffff;
        padding: 10px;
        border: 2px solid #f8d800;
    }}
    .ranking-table td {{
        background-color: rgba(0, 0, 0, 0.85);
        color: #ffffff;
        padding: 10px;
        border: 1px solid #f8d800;
        text-align: center;
    }}
</style>
""", unsafe_allow_html=True)

if st.session_state.state == 'welcome':
    st.markdown('''
    <div class="arcade-card" style="margin-top: 5px;">
        <h1 class="blink-text" style="font-size:1.8rem; margin-bottom:10px;">WELCOME!</h1>
        <h2 style="font-size:1.1rem; color:#00ff00;">QUIZ DA LORYLLAND 🎮</h2>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(f'<img src="{lory_img}" class="lory-avatar-large">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_input = st.text_input("DIGITE SEU NOME PARA O RANKING:", value=st.session_state.player_name,
                                   placeholder="SEU NOME OU NICK")

        if st.button("▶ INICIAR QUIZ"):
            if name_input.strip() == "":
                st.warning("⚠️ Por favor, digite seu nome antes de iniciar!")
            else:
                st.session_state.player_name = name_input.strip().upper()
                st.session_state.state = 'char_select'
                st.rerun()

elif st.session_state.state == 'char_select':
    st.markdown(f'''
    <div class="arcade-card">
        <h2 class="blink-text" style="font-size:1.1rem;">JOGADOR: {st.session_state.player_name}</h2>
        <p style="font-size:0.85rem; color:#00ff00; margin-top:5px;">ESCOLHA SEU PERSONAGEM</p>
    </div>
    ''', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'''
        <div class="arcade-card">
            <img src="{spidey_main}" style="height:220px; object-fit:contain;"><br>
            <h3 style="color:#e60012; font-size:0.9rem; margin-top:12px;">HOMEM-ARANHA</h3>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("▶ SELECIONAR HOMEM-ARANHA"):
            st.session_state.fighter = 'spidey'
            st.session_state.state = 'quiz'
            st.rerun()

    with col2:
        st.markdown(f'''
        <div class="arcade-card">
            <img src="{ironman_main}" style="height:220px; object-fit:contain;"><br>
            <h3 style="color:#f8d800; font-size:0.9rem; margin-top:12px;">HOMEM DE FERRO</h3>
        </div>
        ''', unsafe_allow_html=True)
        if st.button("▶ SELECIONAR HOMEM DE FERRO"):
            st.session_state.fighter = 'ironman'
            st.session_state.state = 'quiz'
            st.rerun()

elif st.session_state.state == 'quiz':
    q_idx = st.session_state.current_q
    q_data = perguntas[q_idx]
    is_spidey = (st.session_state.fighter == 'spidey')

    st.markdown(f'''
    <div style="background:rgba(0,0,0,0.92); border:3px solid #f8d800; padding:10px; color:#f8d800; font-size:0.7rem; display:flex; justify-content:space-between; margin-bottom:15px;">
        <span>PLAYER: {st.session_state.player_name}</span>
        <span>HERÓI: {'HOMEM-ARANHA 🕷️' if is_spidey else 'HOMEM DE FERRO 🦾'}</span>
        <span>ETAPA {q_idx + 1}/{len(perguntas)}</span>
        <span>PONTOS: {st.session_state.score * 100}</span>
    </div>
    ''', unsafe_allow_html=True)

    col_hero, col_q = st.columns([1.1, 1.2])

    with col_hero:
        if st.session_state.last_action == 'correct':
            if is_spidey:
                st.markdown(f'''
                <div class="hero-container-full web-overlay-effect">
                    <p style="color:#ffffff; font-size:0.8rem; margin-bottom:5px;" class="blink-text">🎯 ACERTOU! SOLTOU TEIA!</p>
                    <img src="{spidey_web}" class="hero-img-full">
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="hero-container-full fire-overlay-effect">
                    <p style="color:#ffea00; font-size:0.8rem; margin-bottom:5px;" class="blink-text">🎯 ACERTOU! SOLTOU FOGO!</p>
                    <img src="{ironman_fire}" class="hero-img-full">
                </div>
                ''', unsafe_allow_html=True)

        elif st.session_state.last_action == 'wrong':
            fall_gif = spidey_fall if is_spidey else ironman_fall
            st.markdown(f'''
            <div class="hero-container-full" style="border-color:#ff0000;">
                <p style="color:#ff0000; font-size:0.8rem; margin-bottom:5px;" class="blink-text">💥 ERROU! PERSONAGEM CAINDO!</p>
                <img src="{fall_gif}" class="fall-anim">
            </div>
            ''', unsafe_allow_html=True)

        else:
            main_gif = spidey_main if is_spidey else ironman_main
            st.markdown(f'''
            <div class="hero-container-full">
                <img src="{main_gif}" class="hero-img-full">
            </div>
            ''', unsafe_allow_html=True)

    with col_q:
        if st.session_state.last_action == 'correct':
            st.balloons()

        st.markdown(f'''
        <div class="question-card">
            <p style="font-size:0.85rem; line-height:1.6; margin:0;">{q_data["q"]}</p>
        </div>
        ''', unsafe_allow_html=True)

        if st.session_state.last_action is not None:
            time.sleep(1.2)
            st.session_state.last_action = None

            if st.session_state.current_q + 1 < len(perguntas):
                st.session_state.current_q += 1
                st.rerun()
            else:
                st.session_state.state = 'final'
                st.rerun()
        else:
            for opt in q_data['opts']:
                if st.button(f"▪ {opt}", key=f"btn_{q_idx}_{opt}"):
                    if opt in q_data['ans']:
                        st.session_state.score += 1
                        st.session_state.last_action = 'correct'
                    else:
                        st.session_state.last_action = 'wrong'
                    st.rerun()

elif st.session_state.state == 'final':
    total_points = st.session_state.score * 100
    hero_name = "Homem-Aranha" if st.session_state.fighter == 'spidey' else "Homem de Ferro"

    if st.session_state.score < 10:
        feedback_msg = "Você não conhece nada sobre a Lorylland! 😅"
        msg_color = "#ff4d4d"
    elif st.session_state.score <= 16:
        feedback_msg = "Você até que conhece um pouco sobre a Lorylland! 🙂"
        msg_color = "#f8d800"
    else:
        feedback_msg = "Incrível! Você conhece bastante sobre a Lorylland! 🎉🏆"
        msg_color = "#00ff00"

    if not st.session_state.score_saved:
        save_score(st.session_state.player_name, total_points, hero_name)
        st.session_state.score_saved = True

    st.markdown(f'''
    <div class="arcade-card" style="padding:20px;">
        <h1 class="blink-text" style="font-size:1.5rem;">STAGE CLEAR!</h1>
        <h3 style="color:#00ff00; font-size:1rem; margin:10px 0;">{st.session_state.player_name} - {total_points} PTS</h3>
        <p style="font-size:0.85rem; margin-top:10px;">Você acertou <strong>{st.session_state.score}</strong> de <strong>{len(perguntas)}</strong> perguntas!</p>
        <h2 style="color:{msg_color}; font-size:1rem; margin-top:15px; border-top: 1px dashed #f8d800; padding-top:15px;">
            {feedback_msg}
        </h2>
    </div>
    ''', unsafe_allow_html=True)

    top_scores = get_top_ranking(10)

    ranking_rows = ""
    for idx, (nome, pts, heroi) in enumerate(top_scores, 1):
        trophy = "🥇 " if idx == 1 else "🥈 " if idx == 2 else "🥉 " if idx == 3 else f"{idx}. "
        ranking_rows += f"<tr><td>{trophy}{nome}</td><td>{pts}</td><td>{heroi}</td></tr>"

    st.markdown(f'''
    <div class="arcade-card">
        <h2 style="color:#f8d800; font-size:1.1rem;" class="blink-text">🏆 HALL DA FAMA - TOP 10 🏆</h2>
        <table class="ranking-table">
            <thead>
                <tr>
                    <th>JOGADOR</th>
                    <th>PONTOS</th>
                    <th>HERÓI</th>
                </tr>
            </thead>
            <tbody>
                {ranking_rows}
            </tbody>
        </table>
    </div>
    ''', unsafe_allow_html=True)

    if st.button("🔄 JOGAR NOVAMENTE"):
        st.session_state.state = 'welcome'
        st.session_state.fighter = None
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.last_action = None
        st.session_state.score_saved = False
        st.rerun()