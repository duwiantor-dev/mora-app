import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# =====================
# CONFIG
# =====================
SUPABASE_URL = "PASTE_URL"
SUPABASE_KEY = "PASTE_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")

# =====================
# STYLE (RPG DARK)
# =====================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
.card {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 20px;
    margin-bottom: 20px;
}
.button {
    background: gold;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# =====================
# SESSION
# =====================
if "role" not in st.session_state:
    st.session_state.role = None
if "user" not in st.session_state:
    st.session_state.user = None

# =====================
# LOGIN
# =====================
if st.session_state.role is None:
    st.title("⚔️ Mora App")

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Nama BTS")
        if st.button("Login sebagai BTS"):
            if name:
                # insert kalau belum ada
                supabase.table("bts").upsert({"name": name}).execute()
                st.session_state.role = "BTS"
                st.session_state.user = name
                st.rerun()

    with col2:
        if st.button("Login sebagai MGR"):
            st.session_state.role = "MGR"
            st.session_state.user = "MGR"
            st.rerun()

# =====================
# SIDEBAR
# =====================
else:
    st.sidebar.title("Mora App")

    menu = st.sidebar.radio("Menu", [
        "Summary",
        "Quest",
        "History",
        "Violation",
        "Dashboard MGR"
    ])

# =====================
# FUNCTIONS
# =====================
def get_progress(name):
    res = supabase.table("progress").select("*").eq("bts_name", name).execute()
    return pd.DataFrame(res.data)

def get_quests():
    res = supabase.table("quests").select("*").execute()
    return pd.DataFrame(res.data)

def get_bts():
    res = supabase.table("bts").select("*").execute()
    return pd.DataFrame(res.data)

# =====================
# SUMMARY
# =====================
if menu == "Summary":
    st.title("Summary Performa")

    df = get_progress(st.session_state.user)

    total = len(df)
    done = len(df[df["status"] == "done"])
    pending = total - done

    percent = int((done / total)*100) if total > 0 else 0
    level = done // 5 + 1

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Diberikan", total)
    col2.metric("Selesai", done)
    col3.metric("Belum", pending)
    col4.metric("Persen", f"{percent}%")

    st.markdown(f"### Level: {level}")

# =====================
# QUEST (BTS)
# =====================
if menu == "Quest":
    st.title("Quest")

    quests = get_quests()

    for _, q in quests.iterrows():
        if q["target"] == "all" or q["target"] == st.session_state.user:

            st.markdown(f"""
            <div class="card">
            <h3>{q['title']}</h3>
            <p>{q['description']}</p>
            <p>Difficulty: {q['difficulty']}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Selesaikan {q['id']}"):
                supabase.table("progress").insert({
                    "bts_name": st.session_state.user,
                    "quest_id": q["id"],
                    "status": "done",
                    "completed_at": str(datetime.now())
                }).execute()
                st.success("Quest selesai!")
                st.rerun()

# =====================
# HISTORY
# =====================
if menu == "History":
    st.title("History Quest")

    df = get_progress(st.session_state.user)
    df = df[df["status"] == "done"]

    st.dataframe(df)

# =====================
# VIOLATION
# =====================
if menu == "Violation":
    st.title("Violation")
    st.info("Coming Soon")

# =====================
# DASHBOARD MGR
# =====================
if menu == "Dashboard MGR" and st.session_state.role == "MGR":

    st.title("Dashboard MGR")

    # CREATE QUEST
    st.subheader("Buat Quest")

    title = st.text_input("Judul")
    desc = st.text_area("Deskripsi")
    diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    target = st.selectbox("Target", ["all"] + list(get_bts()["name"]))

    if st.button("Buat Quest"):
        supabase.table("quests").insert({
            "title": title,
            "description": desc,
            "difficulty": diff,
            "reward": 1,
            "target": target
        }).execute()

        st.success("Quest dibuat!")

    st.divider()

    # EDIT BTS NAME
    st.subheader("Edit Nama BTS")

    bts = get_bts()

    if len(bts) > 0:
        selected = st.selectbox("Pilih BTS", bts["name"])
        new_name = st.text_input("Nama Baru")

        if st.button("Update Nama"):
            supabase.table("bts").update({
                "name": new_name
            }).eq("name", selected).execute()

            st.success("Updated!")
            st.rerun()
