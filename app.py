import json
from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title='Task Quest App', page_icon='🎮', layout='wide')

DATA_DIR = Path('data')
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
    },
    {
        'id': 'Q002',
        'title': 'Crash Course',
        'description': 'Selesaikan review SOP onboarding lalu ajukan 3 perbaikan yang paling berdampak untuk tim.',
        'difficulty': 'Normal',
        'reward_level': 1,
        'created_at': '2026-04-06 08:10:00',
    },
    {
        'id': 'Q003',
        'title': 'Sparks Amongst the Pages',
        'description': 'Buat ringkasan pembelajaran proyek berjalan dan unggah dokumentasinya ke knowledge base.',
        'difficulty': 'Hard',
        'reward_level': 1,
        'created_at': '2026-04-06 08:20:00',
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
    max_num = max([int(q['id'].replace('Q', '')) for q in quests], default=0)
    quest = {
        'id': f'Q{max_num + 1:03d}',
        'title': title,
        'description': description,
        'difficulty': difficulty,
        'reward_level': reward_level,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    quests.append(quest)
    save_quests(quests)



def inject_css():
    st.markdown(
        """
        <style>
        :root {
            --gold: #e6cc8d;
            --gold-2: #c7aa63;
            --ink: #243449;
            --panel: rgba(24, 36, 54, 0.80);
            --panel-soft: rgba(255, 247, 229, 0.10);
            --line: rgba(255,255,255,0.12);
            --text: #f6f0dc;
            --muted: #d8d3c6;
            --dark-card: rgba(29, 44, 65, 0.92);
            --cream: rgba(255, 247, 229, 0.82);
        }
        .stApp {
            background:
                radial-gradient(circle at 20% 20%, rgba(255,255,255,0.08), transparent 20%),
                radial-gradient(circle at 80% 15%, rgba(255,214,102,0.08), transparent 16%),
                linear-gradient(135deg, #2c3f57 0%, #526f7e 42%, #8fab78 100%);
            color: var(--text);
        }
        .block-container {
            max-width: 1400px;
            padding-top: 2.3rem;
            padding-bottom: 1.2rem;
        }
        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(31,45,60,0.98), rgba(63,85,98,0.96));
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        div[data-testid="stSidebar"] .block-container {
            padding-top: 1.25rem;
            padding-left: .8rem;
            padding-right: .8rem;
        }
        .app-shell {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 28px;
            padding: 28px 24px 22px 24px;
            margin-top: .65rem;
            backdrop-filter: blur(6px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }
        .login-box, .panel, .detail-card, .metric-card, .quest-item, .stat-bar, .empty-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 22px;
            box-shadow: 0 14px 35px rgba(0,0,0,0.14);
        }
        .login-box { padding: 28px; max-width: 760px; margin: 2rem auto; }
        .panel { padding: 18px; }
        .detail-card { padding: 24px; min-height: 540px; background: rgba(20, 31, 46, 0.95); }
        .metric-card { padding: 16px; text-align: center; min-height: 120px; }
        .quest-item { padding: 12px; margin-bottom: 12px; background: var(--dark-card); }
        .quest-item.active {
            border: 2px solid rgba(230,204,141,0.75);
            background: var(--cream);
            color: #2b3951;
        }
        .quest-item.active .muted,
        .quest-item.active .small-note,
        .quest-item.active .quest-meta {
            color: #53606f !important;
        }
        .headline { font-size: 34px; font-weight: 800; color: var(--gold); line-height: 1.08; }
        .subheadline { font-size: 17px; color: var(--muted); }
        .section-title { font-size: 22px; font-weight: 800; color: var(--gold); margin-bottom: 8px; }
        .muted { color: var(--muted); }
        .small-note { font-size: 13px; opacity: 0.88; }
        .reward-chip {
            display: inline-block;
            padding: 10px 14px;
            border-radius: 14px;
            margin-right: 8px;
            margin-bottom: 8px;
            background: rgba(230,204,141,0.12);
            border: 1px solid rgba(230,204,141,0.42);
            font-weight: 700;
        }
        .sidebar-card {
            padding: 14px;
            border-radius: 18px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
            margin-bottom: 12px;
        }
        .menu-header { font-size: 15px; color: var(--gold); font-weight: 800; margin-bottom: 6px; }
        .menu-caption { font-size: 12px; color: #e1ddcf; opacity: .85; }
        .history-card {
            padding: 18px;
            border-radius: 18px;
            background: rgba(24,36,54,0.78);
            border: 1px solid rgba(255,255,255,0.09);
            margin-bottom: 12px;
        }
        .quest-button-gap { margin-bottom: .2rem; }
        .quest-meta { color: var(--muted); }
        .detail-divider {
            height: 1px;
            background: rgba(255,255,255,0.08);
            margin: 16px 0;
        }
        .detail-description {
            min-height: 180px;
            padding: 16px;
            border-radius: 18px;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.06);
            line-height: 1.7;
            font-size: 17px;
        }
        .detail-hero {
            min-height: 250px;
            border-radius: 22px;
            border: 1px solid rgba(255,255,255,0.08);
            background: linear-gradient(180deg, rgba(38,56,81,0.98), rgba(25,39,59,0.98));
            margin-bottom: 18px;
            display: flex;
            align-items: flex-end;
            padding: 18px;
        }
        .detail-hero-title { font-size: 30px; font-weight: 900; color: var(--gold); }
        .detail-hero-sub { color: var(--muted); margin-top: 4px; }
        .stButton > button {
            width: 100%;
            border-radius: 16px;
            font-weight: 800;
            min-height: 2.95rem;
            box-shadow: none;
        }
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {
            border: 1px solid rgba(255,255,255,0.10);
            background: linear-gradient(180deg, #efdfb1 0%, #d1b16d 100%);
            color: #28344a;
        }
        .stButton > button[kind="secondary"],
        .stFormSubmitButton > button[kind="secondary"] {
            border: 1px solid rgba(255,255,255,0.08);
            background: rgba(29, 44, 65, 0.01);
            color: inherit;
            text-align: left;
            justify-content: flex-start;
            padding-left: 0.6rem;
        }
        .stButton > button:hover { border-color: rgba(255,255,255,0.25); }
        div[data-baseweb="select"] > div,
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {
            border-radius: 14px !important;
            background: rgba(255,255,255,0.92) !important;
        }
        .stProgress > div > div > div > div {
            background: linear-gradient(90deg, #f4e4b2, #d4b46a);
        }
        .icon-badge {
            font-size: 28px;
            width: 56px;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 18px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.08);
            margin: 0 auto 8px auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )



def render_login():
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="headline">Task Quest App</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheadline">Login sebagai GM atau Player untuk masuk ke task tracker bergaya quest game.</div>', unsafe_allow_html=True)
    st.write('')

    col1, col2 = st.columns([1.2, 1])
    with col1:
        username = st.text_input('Nama user', placeholder='contoh: Adit')
    with col2:
        role = st.selectbox('Login sebagai', ['Player', 'GM'])

    st.markdown('<div class="small-note">GM bisa tambah quest baru. Player fokus mengerjakan quest dan naik level.</div>', unsafe_allow_html=True)
    if st.button('Masuk ke App', type='primary'):
        if username.strip():
            user = ensure_user(username.strip(), role)
            st.session_state['username'] = user['username']
            st.session_state['selected_menu'] = 'summary'
            st.rerun()
        st.error('Nama user wajib diisi.')
    st.markdown('</div>', unsafe_allow_html=True)



def render_sidebar(user):
    st.sidebar.markdown('<div class="sidebar-card"><div class="menu-header">In Progress</div><div class="menu-caption">Archon Quests style task tracker</div></div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<div class="sidebar-card">'
        f'<div class="icon-badge">👤</div>'
        f'<div style="text-align:center;font-weight:800;">{user["username"]}</div>'
        f'<div class="menu-caption" style="text-align:center;">Role: {user["role"]} · Level {user["level"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    options = {
        'summary': '✦  Summary Performa',
        'quests': '◈  Daftar Quest',
        'violation': '⚠  Violation',
        'history': '🕘  History Quest',
        'dashboard': '✚  Dashboard GM',
    }

    labels = list(options.values())
    reverse = {v: k for k, v in options.items()}
    current = options.get(st.session_state.get('selected_menu', 'summary'))
    chosen = st.sidebar.radio('Menu', labels, index=labels.index(current), label_visibility='collapsed')
    st.session_state['selected_menu'] = reverse[chosen]

    st.sidebar.markdown('<div class="sidebar-card"><div class="menu-caption">Quest selesai akan hilang dari daftar quest dan pindah ke history quest.</div></div>', unsafe_allow_html=True)
    if st.sidebar.button('Logout', type='primary'):
        st.session_state.clear()
        st.rerun()



def render_summary(user, quests):
    completed_ids = set(user['completed_quests'])
    active = [q for q in quests if q['id'] not in completed_ids]
    done = [q for q in quests if q['id'] in completed_ids]
    completion_rate = int((len(done) / len(quests)) * 100) if quests else 0
    progress_to_next = (user['level'] % 5) / 5

    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="headline">Summary Performa</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheadline">Ringkasan progress player, level saat ini, dan performa penyelesaian quest.</div>', unsafe_allow_html=True)
    st.write('')

    c1, c2, c3, c4 = st.columns(4)
    metric_data = [
        ('⭐', 'Level Saat Ini', user['level']),
        ('📜', 'Quest Aktif', len(active)),
        ('✅', 'Quest Selesai', len(done)),
        ('📈', 'Completion Rate', f'{completion_rate}%'),
    ]
    for col, (icon, title, value) in zip([c1, c2, c3, c4], metric_data):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:30px;">{icon}</div>'
                f'<div class="small-note">{title}</div>'
                f'<div style="font-size:34px;font-weight:900;color:var(--gold);margin-top:8px;">{value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.write('')
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Progress Level</div>', unsafe_allow_html=True)
        st.progress(progress_to_next if progress_to_next > 0 else 0.02)
        st.markdown('<div class="small-note">Setiap 1 quest selesai akan menambah level sesuai reward.</div>', unsafe_allow_html=True)
        st.write('')
        st.markdown('<div class="section-title">Recent Activity</div>', unsafe_allow_html=True)
        if done:
            for q in done[-3:][::-1]:
                st.markdown(f'<div class="history-card"><b>{q["title"]}</b><br><span class="small-note">Reward diterima: +{q.get("reward_level", 1)} level</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-card" style="padding:18px;">Belum ada quest yang selesai.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Status Player</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="reward-chip">Role: {user["role"]}</span><span class="reward-chip">Joined: {user["created_at"][:10]}</span>', unsafe_allow_html=True)
        st.write('')
        st.markdown('<div class="section-title">Ringkasan</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="small-note">'
            'Menu 1 berisi summary performa.<br>'
            'Menu 2 berisi daftar quest dan panel detail di kanan.<br>'
            'Menu 3 violation masih coming soon.<br>'
            'Menu 4 history quest.<br>'
            'Menu 5 dashboard tambah quest untuk GM.'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)



def render_quests(user, quests):
    completed_ids = set(user['completed_quests'])
    active_quests = [q for q in quests if q['id'] not in completed_ids]

    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="headline">Daftar Quest</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheadline">Klik nama quest di panel kiri. Detail deskripsi tugas sekarang tampil di kotak hitam besar sebelah kanan.</div>', unsafe_allow_html=True)
    st.write('')

    if not active_quests:
        st.markdown('<div class="empty-card" style="padding:18px;">Semua quest sudah selesai. Cek History Quest untuk melihat daftar yang sudah done.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    valid_ids = [q['id'] for q in active_quests]
    if st.session_state.get('selected_quest_id') not in valid_ids:
        st.session_state['selected_quest_id'] = active_quests[0]['id']

    left, right = st.columns([1.02, 1.58], gap='large')
    with left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Archon Quests</div>', unsafe_allow_html=True)
        for q in active_quests:
            active_class = ' active' if q['id'] == st.session_state['selected_quest_id'] else ''
            st.markdown(f'<div class="quest-item{active_class}">', unsafe_allow_html=True)
            if st.button(q['title'], key=f'select_{q["id"]}', use_container_width=True, type='secondary'):
                st.session_state['selected_quest_id'] = q['id']
                st.rerun()
            st.markdown(
                f'<div class="quest-meta">Reward +{q.get("reward_level", 1)} level</div>'
                f'<div class="small-note">Difficulty: {q.get("difficulty", "Normal")} · ID {q["id"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    selected = next(q for q in active_quests if q['id'] == st.session_state['selected_quest_id'])
    with right:
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="detail-hero">'
            f'<div>'
            f'<div class="detail-hero-title">{selected["title"]}</div>'
            f'<div class="detail-hero-sub">Quest aktif · ID {selected["id"]} · Reward +{selected.get("reward_level", 1)} level</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-title">Deskripsi Tugas</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-description">{selected["description"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="detail-divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Reward Quest</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="reward-chip">+{selected.get("reward_level", 1)} Level</span>'
            f'<span class="reward-chip">{selected.get("difficulty", "Normal")}</span>'
            f'<span class="reward-chip">Created {selected["created_at"][:10]}</span>',
            unsafe_allow_html=True,
        )
        st.write('')
        st.info('Kerjain 1 tugas = naik level. Setelah selesai, quest akan pindah ke History Quest.')
        if st.button('Tandai Quest Selesai', key='complete_selected', type='primary'):
            complete_quest(user['username'], selected['id'])
            st.success(f'Quest {selected["title"]} selesai. Level bertambah.')
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



def render_violation():
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="headline">Violation</div>', unsafe_allow_html=True)
    st.markdown('<div class="detail-card" style="display:flex;align-items:center;justify-content:center;text-align:center;">', unsafe_allow_html=True)
    st.markdown('<div><div style="font-size:56px;">⚠</div><div class="headline" style="font-size:30px;">COMING SOON</div><div class="subheadline">Bagian violation belum kita bahas. Nanti bisa diisi aturan, poin pelanggaran, dan konsekuensi.</div></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)



def render_history(user, quests):
    done = [q for q in quests if q['id'] in set(user['completed_quests'])]
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="headline">History Quest</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheadline">Quest yang sudah done akan hilang dari menu daftar quest dan pindah ke sini.</div>', unsafe_allow_html=True)
    st.write('')

    if not done:
        st.markdown('<div class="empty-card" style="padding:18px;">Belum ada quest yang selesai.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return

    for q in done[::-1]:
        st.markdown(
            f'<div class="history-card">'
            f'<div style="font-size:22px;font-weight:800;color:var(--gold);">{q["title"]}</div>'
            f'<div class="muted" style="margin-top:6px;">{q["description"]}</div>'
            f'<div class="small-note" style="margin-top:10px;">Status: DONE · Reward diterima: +{q.get("reward_level", 1)} level</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)



def render_dashboard(user):
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown('<div class="headline">Dashboard Tambah Quest</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheadline">Menu untuk menambah quest baru. Hanya GM yang bisa akses penuh.</div>', unsafe_allow_html=True)
    st.write('')

    if user['role'] != 'GM':
        st.warning('Menu ini khusus GM. Login sebagai GM untuk menambah quest baru.')
        st.markdown('</div>', unsafe_allow_html=True)
        return

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    with st.form('add_quest_form'):
        title = st.text_input('Judul quest')
        description = st.text_area('Deskripsi tugas', height=160)
        c1, c2 = st.columns(2)
        with c1:
            difficulty = st.selectbox('Difficulty', ['Easy', 'Normal', 'Hard'])
        with c2:
            reward_level = st.number_input('Reward level', min_value=1, max_value=10, value=1, step=1)
        submitted = st.form_submit_button('Tambah Quest Baru', type='primary')

    if submitted:
        if title.strip() and description.strip():
            add_quest(title.strip(), description.strip(), difficulty, int(reward_level))
            st.success('Quest baru berhasil ditambahkan.')
        else:
            st.error('Judul dan deskripsi wajib diisi.')
    st.markdown('</div></div>', unsafe_allow_html=True)



def main():
    init_storage()
    inject_css()
    st.session_state.setdefault('selected_menu', 'summary')

    if 'username' not in st.session_state:
        render_login()
        return

    user = get_current_user()
    if user is None:
        st.session_state.clear()
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
