import os
from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client


# =====================
# PAGE CONFIG
# =====================
st.set_page_config(
    page_title="Mora App",
    page_icon="⚔️",
    layout="wide",
)

# =====================
# CONFIG (SECRETS / ENV)
# =====================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("SUPABASE_URL atau SUPABASE_KEY belum terbaca dari Streamlit Secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =====================
# STYLE
# =====================
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #071120 0%, #0c1830 45%, #13233b 100%);
            color: white;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .mora-title {
            font-size: 48px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #f8fafc;
        }

        .mora-subtitle {
            color: #b8c1d1;
            margin-bottom: 20px;
        }

        .card {
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 22px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18);
        }

        .quest-title {
            font-size: 28px;
            font-weight: 800;
            color: #f8fafc;
            margin-bottom: 8px;
        }

        .soft-text {
            color: #cbd5e1;
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            margin-top: 8px;
            margin-bottom: 8px;
        }

        .badge-easy {
            background: rgba(80, 200, 120, 0.18);
            color: #9af0b5;
            border: 1px solid rgba(80, 200, 120, 0.24);
        }

        .badge-medium {
            background: rgba(240, 200, 90, 0.18);
            color: #f8de8a;
            border: 1px solid rgba(240, 200, 90, 0.24);
        }

        .badge-hard {
            background: rgba(220, 80, 120, 0.18);
            color: #ff9ab9;
            border: 1px solid rgba(220, 80, 120, 0.24);
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.06);
            border-radius: 20px;
            padding: 18px;
            border: 1px solid rgba(255,255,255,0.07);
        }

        .section-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =====================
# SESSION STATE
# =====================
if "role" not in st.session_state:
    st.session_state.role = None

if "user" not in st.session_state:
    st.session_state.user = None

if "selected_quest_id" not in st.session_state:
    st.session_state.selected_quest_id = None


# =====================
# HELPERS
# =====================
def difficulty_badge(diff: str) -> str:
    diff_lower = (diff or "").lower()

    if diff_lower == "easy":
        return '<span class="badge badge-easy">Easy</span>'
    if diff_lower == "medium":
        return '<span class="badge badge-medium">Medium</span>'
    if diff_lower == "hard":
        return '<span class="badge badge-hard">Hard</span>'
    return f'<span class="badge">{diff}</span>'


def calculate_level(done_count: int) -> int:
    return (done_count // 5) + 1


def safe_df(data) -> pd.DataFrame:
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)


def get_bts() -> pd.DataFrame:
    res = supabase.table("bts").select("*").order("created_at").execute()
    return safe_df(res.data)


def get_quests() -> pd.DataFrame:
    res = supabase.table("quests").select("*").order("created_at", desc=True).execute()
    return safe_df(res.data)


def get_progress_by_bts(bts_name: str) -> pd.DataFrame:
    res = (
        supabase.table("progress")
        .select("*")
        .eq("bts_name", bts_name)
        .order("completed_at", desc=True)
        .execute()
    )
    return safe_df(res.data)


def get_done_quest_ids_for_bts(bts_name: str) -> set:
    df = get_progress_by_bts(bts_name)
    if df.empty:
        return set()

    done_df = df[df["status"] == "done"] if "status" in df.columns else pd.DataFrame()
    if done_df.empty or "quest_id" not in done_df.columns:
        return set()

    return set(done_df["quest_id"].astype(str).tolist())


def get_available_quests_for_bts(bts_name: str) -> pd.DataFrame:
    quests_df = get_quests()
    if quests_df.empty:
        return pd.DataFrame()

    visible_df = quests_df[
        (quests_df["target"] == "all") | (quests_df["target"] == bts_name)
    ].copy()

    done_ids = get_done_quest_ids_for_bts(bts_name)
    if done_ids:
        visible_df = visible_df[~visible_df["id"].astype(str).isin(done_ids)]

    return visible_df


def create_bts_if_not_exists(name: str) -> None:
    existing = supabase.table("bts").select("name").eq("name", name).execute()
    if not existing.data:
        supabase.table("bts").insert({"name": name}).execute()


def mark_quest_done(bts_name: str, quest_id: str) -> None:
    existing = (
        supabase.table("progress")
        .select("*")
        .eq("bts_name", bts_name)
        .eq("quest_id", quest_id)
        .eq("status", "done")
        .execute()
    )

    if existing.data:
        return

    supabase.table("progress").insert(
        {
            "bts_name": bts_name,
            "quest_id": quest_id,
            "status": "done",
            "completed_at": datetime.utcnow().isoformat(),
        }
    ).execute()


def rename_bts(old_name: str, new_name: str) -> None:
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Nama baru tidak boleh kosong.")

    # cek unique
    exists = supabase.table("bts").select("name").eq("name", new_name).execute()
    if exists.data:
        raise ValueError("Nama BTS sudah dipakai.")

    supabase.table("bts").update({"name": new_name}).eq("name", old_name).execute()
    supabase.table("progress").update({"bts_name": new_name}).eq("bts_name", old_name).execute()


# =====================
# LOGIN PAGE
# =====================
if st.session_state.role is None:
    st.markdown('<div class="mora-title">⚔️ Mora App</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="mora-subtitle">Login sebagai BTS atau MGR</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.4, 1])

    with left:
        name = st.text_input("Nama BTS")

        if st.button("Login sebagai BTS", use_container_width=False):
            clean_name = name.strip()
            if not clean_name:
                st.warning("Masukkan nama BTS dulu.")
            else:
                try:
                    create_bts_if_not_exists(clean_name)
                    st.session_state.role = "BTS"
                    st.session_state.user = clean_name
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal login BTS: {e}")

    with right:
        st.write("")
        st.write("")
        if st.button("Login sebagai MGR", use_container_width=False):
            st.session_state.role = "MGR"
            st.session_state.user = "MGR"
            st.rerun()

    st.stop()


# =====================
# SIDEBAR
# =====================
with st.sidebar:
    st.title("Mora App")
    st.caption(f"Role: {st.session_state.role}")
    if st.session_state.user:
        st.write(f"User: **{st.session_state.user}**")

    if st.session_state.role == "BTS":
        menu = st.radio(
            "Menu",
            ["Summary", "Quest", "History", "Violation"],
        )
    else:
        menu = st.radio(
            "Menu",
            ["Dashboard MGR", "Violation"],
        )

    st.divider()

    if st.button("Logout", use_container_width=True):
        st.session_state.role = None
        st.session_state.user = None
        st.session_state.selected_quest_id = None
        st.rerun()


# =====================
# BTS - SUMMARY
# =====================
if st.session_state.role == "BTS" and menu == "Summary":
    st.markdown('<div class="section-title">Summary Performa</div>', unsafe_allow_html=True)

    progress_df = get_progress_by_bts(st.session_state.user)
    total = len(progress_df)
    done = len(progress_df[progress_df["status"] == "done"]) if not progress_df.empty else 0
    pending = max(total - done, 0)
    percent = int((done / total) * 100) if total > 0 else 0
    level = calculate_level(done)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quest Diberikan", total)
    c2.metric("Quest Selesai", done)
    c3.metric("Belum Selesai", pending)
    c4.metric("Persentase", f"{percent}%")

    st.markdown(f"### Level Saat Ini: {level}")

    st.progress(percent / 100 if percent > 0 else 0)


# =====================
# BTS - QUEST
# =====================
elif st.session_state.role == "BTS" and menu == "Quest":
    st.markdown('<div class="section-title">Archon Quests</div>', unsafe_allow_html=True)

    quests_df = get_available_quests_for_bts(st.session_state.user)

    if quests_df.empty:
        st.info("Belum ada quest aktif.")
    else:
        col_left, col_right = st.columns([1.05, 1.45])

        with col_left:
            st.subheader("Daftar Quest")

            for _, row in quests_df.iterrows():
                quest_id = str(row["id"])
                title = row.get("title", "-")
                description = row.get("description", "-")
                difficulty = row.get("difficulty", "-")

                with st.container():
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="quest-title">{title}</div>
                            <div class="soft-text">{description}</div>
                            {difficulty_badge(difficulty)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(f"Pilih: {title}", key=f"pick_{quest_id}"):
                        st.session_state.selected_quest_id = quest_id
                        st.rerun()

        with col_right:
            selected_df = quests_df.copy()

            if st.session_state.selected_quest_id:
                selected_df = selected_df[
                    selected_df["id"].astype(str) == st.session_state.selected_quest_id
                ]

            if selected_df.empty:
                selected_df = quests_df.head(1)

            selected = selected_df.iloc[0]

            st.markdown(
                f"""
                <div class="card">
                    <div class="section-title" style="margin-bottom:6px;">{selected.get("title", "-")}</div>
                    <div style="font-size:20px; color:#f6d86d; margin-bottom:16px;">
                        Task Area · Operational Board
                    </div>

                    <div class="card" style="margin-top:10px;">
                        <h3>Deskripsi Tugas</h3>
                        <div style="font-size:20px; line-height:1.7;">
                            {selected.get("description", "-")}
                        </div>
                        <div style="margin-top:12px;">
                            {difficulty_badge(selected.get("difficulty", "-"))}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            done_count = len(get_done_quest_ids_for_bts(st.session_state.user))
            next_level = calculate_level(done_count + 1)

            c1, c2 = st.columns([1, 1.3])
            with c1:
                st.markdown(
                    f"""
                    <div class="card">
                        <div class="soft-text">Reward</div>
                        <div style="font-size:18px;">+1 Quest Selesai</div>
                        <div style="font-size:28px; font-weight:800;">Next Level: {next_level}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c2:
                if st.button("Selesaikan Quest", use_container_width=True):
                    try:
                        mark_quest_done(st.session_state.user, str(selected["id"]))
                        st.success("Quest berhasil diselesaikan.")
                        st.session_state.selected_quest_id = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyelesaikan quest: {e}")


# =====================
# BTS - HISTORY
# =====================
elif st.session_state.role == "BTS" and menu == "History":
    st.markdown('<div class="section-title">History Quest</div>', unsafe_allow_html=True)

    progress_df = get_progress_by_bts(st.session_state.user)
    if progress_df.empty:
        st.info("Belum ada history quest.")
    else:
        done_df = progress_df[progress_df["status"] == "done"].copy()
        if done_df.empty:
            st.info("Belum ada quest yang selesai.")
        else:
            quests_df = get_quests()
            if not quests_df.empty:
                merged = done_df.merge(
                    quests_df[["id", "title", "description", "difficulty"]],
                    left_on="quest_id",
                    right_on="id",
                    how="left",
                )
            else:
                merged = done_df

            for _, row in merged.iterrows():
                title = row.get("title", "Quest")
                desc = row.get("description", "-")
                diff = row.get("difficulty", "-")
                completed_at = row.get("completed_at", "-")

                st.markdown(
                    f"""
                    <div class="card">
                        <div class="quest-title">{title}</div>
                        <div class="soft-text">{desc}</div>
                        <div class="soft-text" style="margin-top:10px;">Selesai: {completed_at}</div>
                        <div style="margin-top:8px;">{difficulty_badge(diff)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =====================
# MGR - DASHBOARD
# =====================
elif st.session_state.role == "MGR" and menu == "Dashboard MGR":
    st.markdown('<div class="section-title">Dashboard MGR</div>', unsafe_allow_html=True)

    left, right = st.columns([1.1, 1.4])

    with left:
        st.markdown("### Bikin Quest Baru")

        title = st.text_input("Judul Tugas")
        description = st.text_area("Deskripsi Tugas", height=180)
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

        bts_df = get_bts()
        target_options = ["all"]
        if not bts_df.empty and "name" in bts_df.columns:
            target_options.extend(bts_df["name"].tolist())

        target = st.selectbox("Quest Untuk", target_options)

        if st.button("Buat Quest Baru", use_container_width=True):
            if not title.strip() or not description.strip():
                st.warning("Judul dan deskripsi wajib diisi.")
            else:
                try:
                    supabase.table("quests").insert(
                        {
                            "title": title.strip(),
                            "description": description.strip(),
                            "difficulty": difficulty,
                            "reward": 1,
                            "target": target,
                        }
                    ).execute()
                    st.success("Quest berhasil dibuat.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal membuat quest: {e}")

        st.divider()
        st.markdown("### Edit Nama BTS")

        if bts_df.empty:
            st.info("Belum ada BTS.")
        else:
            selected_bts = st.selectbox("Pilih BTS", bts_df["name"].tolist())
            new_name = st.text_input("Nama Baru BTS")

            if st.button("Update Nama BTS", use_container_width=True):
                try:
                    rename_bts(selected_bts, new_name)
                    st.success("Nama BTS berhasil diupdate.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    with right:
        st.markdown("### Preview Quest")

        preview_title = title.strip() if title.strip() else "Belum diisi"
        preview_desc = description.strip() if description.strip() else "Deskripsi quest akan tampil di sini."
        preview_target = "Semua BTS" if target == "all" else target

        st.markdown(
            f"""
            <div class="card">
                <div class="section-title" style="margin-bottom:8px;">Dashboard MGR</div>
                <div class="soft-text" style="font-size:20px; margin-bottom:22px;">
                    Buat quest baru lalu tentukan apakah quest diberikan untuk semua BTS atau BTS tertentu.
                </div>

                <div class="card">
                    <div class="soft-text">Judul Quest</div>
                    <div style="font-size:28px; font-weight:800;">{preview_title}</div>
                </div>

                <div class="card">
                    <div class="soft-text">Target BTS</div>
                    <div style="font-size:24px; font-weight:700;">{preview_target}</div>
                </div>

                <div class="card">
                    <div class="soft-text">Preview Deskripsi</div>
                    <div style="font-size:20px; line-height:1.7;">{preview_desc}</div>
                    <div style="margin-top:12px;">{difficulty_badge(difficulty)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### Summary Performa Semua BTS")

        if bts_df.empty:
            st.info("Belum ada data BTS.")
        else:
            for _, bts_row in bts_df.iterrows():
                name = bts_row["name"]
                progress_df = get_progress_by_bts(name)

                total = len(progress_df)
                done = len(progress_df[progress_df["status"] == "done"]) if not progress_df.empty else 0
                pending = max(total - done, 0)
                percent = int((done / total) * 100) if total > 0 else 0
                level = calculate_level(done)

                st.markdown(
                    f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-size:28px; font-weight:800;">{name}</div>
                            <div>{level_badge(level) if False else f'<span class="badge badge-medium">Level {level}</span>'}</div>
                        </div>
                        <div class="soft-text" style="margin-top:10px;">
                            Diberikan: {total} &nbsp; | &nbsp; Selesai: {done} &nbsp; | &nbsp; Belum: {pending} &nbsp; | &nbsp; Persentase: {percent}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# =====================
# VIOLATION
# =====================
elif menu == "Violation":
    st.markdown('<div class="section-title">Violation</div>', unsafe_allow_html=True)
    st.info("Coming Soon")
