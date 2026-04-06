import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
QUESTS_FILE = DATA_DIR / 'quests.json'
USERS_FILE = DATA_DIR / 'users.json'

DEFAULT_QUESTS = [
    {
        'id': 'Q001',
        'title': 'Winds of the Past',
        'description': 'Rapikan backlog tim minggu ini, pastikan semua task prioritas tinggi punya PIC dan deadline yang jelas.',
        'difficulty': 'Normal',
        'reward_level': 1,
        'created_at': '2026-04-06 08:00:00',
        'status': 'active',
    },
    {
        'id': 'Q002',
        'title': 'Crash Course',
        'description': 'Selesaikan review SOP onboarding lalu ajukan 3 perbaikan yang paling berdampak untuk tim.',
        'difficulty': 'Normal',
        'reward_level': 1,
        'created_at': '2026-04-06 08:10:00',
        'status': 'active',
    },
    {
        'id': 'Q003',
        'title': 'Sparks Amongst the Pages',
        'description': 'Buat ringkasan pembelajaran proyek berjalan dan unggah dokumentasinya ke knowledge base.',
        'difficulty': 'Hard',
        'reward_level': 1,
        'created_at': '2026-04-06 08:20:00',
        'status': 'active',
    },
]


def load_json(path: Path, default):
    if not path.exists():
        save_json(path, default)
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path: Path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def init_storage():
    load_json(QUESTS_FILE, DEFAULT_QUESTS)
    load_json(USERS_FILE, {})


def get_quests():
    return load_json(QUESTS_FILE, DEFAULT_QUESTS)


def save_quests(quests):
    save_json(QUESTS_FILE, quests)


def get_users():
    return load_json(USERS_FILE, {})


def save_users(users):
    save_json(USERS_FILE, users)


def ensure_user(username: str, role: str):
    users = get_users()
    if username not in users:
        users[username] = {
            'username': username,
            'role': role,
            'level': 1,
            'completed_quests': [],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    else:
        users[username]['role'] = role
    save_users(users)
    return users[username]


def get_current_user():
    username = st.session_state.get('username')
    if not username:
        return None
    return get_users().get(username)


def complete_quest(username: str, quest_id: str):
    users = get_users()
    quests = get_quests()
    user = users[username]
    if quest_id not in user['completed_quests']:
        user['completed_quests'].append(quest_id)
        reward = next((q.get('reward_level', 1) for q in quests if q['id'] == quest_id), 1)
        user['level'] += reward
        save_users(users)


def add_quest(title: str, description: str, difficulty: str, reward_level: int):
    quests = get_quests()
    next_num = len(quests) + 1
    quest = {
        'id': f'Q{next_num:03d}',
        'title': title,
        'description': description,
        'difficulty': difficulty,
        'reward_level': reward_level,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'active',
    }
    quests.append(quest)
    save_quests(quests)


def inject_css():
    st.markdown(
        '''
        <style>
        .stApp {
            background: linear-gradient(135deg, #24324a 0%, #334a63 35%, #88a879 100%);
            color: #f7f1dd;
        }
        .block-container {
            max-width: 1350px;
            padding-top: 1.2rem;
            padding-bottom: 1rem;
        }
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(22,34,49,0.97), rgba(45,67,85,0.95));
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        .login-card, .panel, .quest-card, .detail-card, .metric-card {
            background: rgba(19, 30, 46, 0.72);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        }
        .login-card { padding: 24px; }
        .panel { padding: 18px; }
        .quest-card { padding: 14px 18px; margin-bottom: 12px; }
        .detail-card { padding: 22px; min-height: 520px; }
        .metric-card { padding: 18px; text-align: center; min-height: 120px; }
        .quest-title { font-size: 30px; font-weight: 700; color: #f0dfb0; margin-bottom: 4px; }
        .section-title { font-size: 26px; font-weight: 700; color: #f0dfb0; margin-bottom: 12px; }
        .subtle { color: #d7d9d8; opacity: 0.92; }
        .reward-badge {
            display: inline-block;
            padding: 8px 12px;
            margin-right: 8px;
            border-radius: 12px;
            background: rgba(240, 223, 176, 0.18);
            border: 1px solid rgba(240, 223, 176, 0.38);
            font-weight: 600;
        }
        .menu-note {
            padding: 10px 14px;
            border-radius: 12px;
            background: rgba(240,223,176,0.08);
            border: 1px solid rgba(240,223,176,0.18);
            margin-bottom: 8px;
        }
        .tiny { font-size: 13px; opacity: 0.8; }
        .stButton > button {
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.12);
            background: linear-gradient(180deg, #f1e2b2, #d8be78);
            color: #24324a;
            font-weight: 700;
        }
        .stButton > button:hover { border-color: rgba(255,255,255,0.3); }
        .sidebar-icon {
            font-size: 20px;
            margin-right: 8px;
        }
        </style>
        ''',
        unsafe_allow_html=True,
    )


def render_login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="quest-title">Task Quest App</div>', unsafe_allow_html=True)
    st.markdown('<p class="subtle">Masuk sebagai <b>GM</b> atau <b>Player</b>. Tampilan dibuat terinspirasi dari menu quest seperti gambar yang kamu kirim.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input('Nama User', placeholder='contoh: Adit')
    with col2:
        role = st.selectbox('Login sebagai', ['Player', 'GM'])

    if st.button('Login'):
        if username.strip():
            user = ensure_user(username.strip(), role)
            st.session_state['username'] = user['username']
            st.session_state['role'] = role
            st.session_state['selected_menu'] = 'summary'
            st.rerun()
        else:
            st.error('Masukkan nama user dulu.')
    st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar(user):
    st.sidebar.markdown('## In Progress')
    st.sidebar.markdown(f'**{user["username"]}**  \\nRole: **{user["role"]}**  \\nLevel: **{user["level"]}**')
    st.sidebar.markdown('---')

    menu_items = [
        ('summary', '✦', 'Menu 1 · Summary Performa'),
        ('quests', '◈', 'Menu 2 · Daftar Quest'),
        ('violation', '⚠', 'Menu 3 · Violation'),
        ('history', '🕘', 'Menu 4 · History Quest'),
        ('dashboard', '✚', 'Menu 5 · Dashboard GM'),
    ]

    for key, icon, label in menu_items:
        if st.sidebar.button(f'{icon}  {label}', use_container_width=True):
            st.session_state['selected_menu'] = key

    st.sidebar.markdown('---')
    st.sidebar.markdown('<div class="menu-note">Ada 5 menu di kiri, sesuai brief kamu.</div>', unsafe_allow_html=True)
    if st.sidebar.button('Logout', use_container_width=True):
        for key in ['username', 'role', 'selected_menu']:
            st.session_state.pop(key, None)
        st.rerun()


def render_summary(user, quests):
    completed = user['completed_quests']
    active = [q for q in quests if q['id'] not in completed]
    done = [q for q in quests if q['id'] in completed]
    completion_rate = 0 if not quests else int((len(done) / len(quests)) * 100)

    st.markdown('<div class="quest-title">Summary Performa</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, 'Level Saat Ini', user['level']),
        (c2, 'Quest Aktif', len(active)),
        (c3, 'Quest Selesai', len(done)),
        (c4, 'Completion Rate', f'{completion_rate}%'),
    ]
    for col, title, value in metrics:
        with col:
            st.markdown(f'<div class="metric-card"><div class="tiny">{title}</div><div style="font-size:34px;font-weight:800;color:#f0dfb0;margin-top:12px;">{value}</div></div>', unsafe_allow_html=True)

    st.markdown('')
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('### Ringkasan')
    st.write(
        'Menu ini menampilkan progress utama player. Setiap 1 quest yang selesai akan menambah level sesuai reward quest. '
        'Quest yang selesai otomatis hilang dari daftar quest aktif dan pindah ke history quest.'
    )
    if done:
        st.write('Quest terakhir yang selesai:')
        for q in done[-3:][::-1]:
            st.markdown(f'- **{q["title"]}** · +{q.get("reward_level", 1)} level')
    else:
        st.info('Belum ada quest yang selesai.')
    st.markdown('</div>', unsafe_allow_html=True)


def render_quests(user, quests):
    st.markdown('<div class="quest-title">Daftar Quest</div>', unsafe_allow_html=True)
    active_quests = [q for q in quests if q['id'] not in user['completed_quests']]

    if not active_quests:
        st.success('Semua quest sudah selesai.')
        return

    if 'selected_quest_id' not in st.session_state or st.session_state['selected_quest_id'] not in [q['id'] for q in active_quests]:
        st.session_state['selected_quest_id'] = active_quests[0]['id']

    left, right = st.columns([1.15, 1.7])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('### Quest List')
        for q in active_quests:
            with st.container():
                st.markdown(f'<div class="quest-card"><div style="font-size:24px;font-weight:700;color:#f0dfb0;">{q["title"]}</div><div class="subtle">Reward: +{q.get("reward_level",1)} level · Difficulty: {q.get("difficulty","Normal")}</div></div>', unsafe_allow_html=True)
                if st.button(f'Pilih {q["id"]}', key=f'select_{q["id"]}', use_container_width=True):
                    st.session_state['selected_quest_id'] = q['id']
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    selected = next((q for q in active_quests if q['id'] == st.session_state['selected_quest_id']), active_quests[0])
    with right:
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="quest-title" style="font-size:24px;">{selected["title"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="subtle">ID Quest: {selected["id"]} · Dibuat: {selected["created_at"]}</p>', unsafe_allow_html=True)
        st.markdown('### Deskripsi Tugas')
        st.write(selected['description'])
        st.markdown('### Reward Quest')
        st.markdown(
            f'<span class="reward-badge">+{selected.get("reward_level",1)} Level</span>'
            f'<span class="reward-badge">{selected.get("difficulty","Normal")}</span>',
            unsafe_allow_html=True,
        )
        st.markdown('')
        st.info('Kerjain 1 tugas = naik level. Setelah di-complete, quest akan pindah ke History Quest.')
        if st.button('Tandai Quest Selesai', key='complete_selected'):
            complete_quest(user['username'], selected['id'])
            st.success(f'Quest {selected["title"]} selesai. Level bertambah!')
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def render_violation():
    st.markdown('<div class="quest-title">Violation</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><h2 style="text-align:center;margin-top:40px;">COMING SOON</h2><p style="text-align:center;" class="subtle">Bagian violation belum dibahas. Nanti bisa kita isi aturan, poin pelanggaran, dan konsekuensinya.</p></div>', unsafe_allow_html=True)


def render_history(user, quests):
    st.markdown('<div class="quest-title">History Quest</div>', unsafe_allow_html=True)
    done = [q for q in quests if q['id'] in user['completed_quests']]
    if not done:
        st.info('Belum ada history quest.')
        return
    for q in done[::-1]:
        st.markdown(
            f'<div class="quest-card"><div style="font-size:22px;font-weight:700;color:#f0dfb0;">{q["title"]}</div>'
            f'<div class="subtle">{q["description"]}</div>'
            f'<div class="tiny" style="margin-top:10px;">Status: DONE · Reward diterima: +{q.get("reward_level",1)} level</div></div>',
            unsafe_allow_html=True,
        )


def render_dashboard(user):
    st.markdown('<div class="quest-title">Dashboard Tambah Quest</div>', unsafe_allow_html=True)
    if user['role'] != 'GM':
        st.warning('Menu ini khusus GM. Login sebagai GM untuk menambah quest baru.')
        return

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.write('Gunakan form ini untuk menambah quest baru ke menu Daftar Quest.')
    with st.form('add_quest_form'):
        title = st.text_input('Judul Quest')
        description = st.text_area('Deskripsi Tugas', height=160)
        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.selectbox('Difficulty', ['Easy', 'Normal', 'Hard'])
        with col2:
            reward_level = st.number_input('Reward Level', min_value=1, max_value=10, value=1, step=1)
        submitted = st.form_submit_button('Tambah Quest')

    if submitted:
        if title.strip() and description.strip():
            add_quest(title.strip(), description.strip(), difficulty, int(reward_level))
            st.success('Quest baru berhasil ditambahkan.')
        else:
            st.error('Judul dan deskripsi wajib diisi.')
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    st.set_page_config(page_title='Task Quest App', page_icon='🎮', layout='wide')
    init_storage()
    inject_css()

    st.session_state.setdefault('selected_menu', 'summary')

    if 'username' not in st.session_state:
        render_login()
        return

    user = get_current_user()
    if user is None:
        for key in ['username', 'role', 'selected_menu']:
            st.session_state.pop(key, None)
        st.rerun()

    quests = get_quests()
    render_sidebar(user)

    menu = st.session_state.get('selected_menu', 'summary')
    if menu == 'summary':
        render_summary(user, quests)
    elif menu == 'quests':
        render_quests(user, quests)
    elif menu == 'violation':
        render_violation()
    elif menu == 'history':
        render_history(user, quests)
    elif menu == 'dashboard':
        render_dashboard(user)


if __name__ == '__main__':
    main()
