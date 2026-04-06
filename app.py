import json
import math
import os
from datetime import date, datetime
from typing import Dict, List

import pandas as pd
import streamlit as st

APP_NAME = "MORA = Monitor Online Agres"
DATA_FILE = "mora_data.json"
ADMIN_PASSWORD = "admin123"
DEFAULT_PICS = ["JEJEN", "OLA", "JUMIO"]
DEFAULT_QUESTS = [
    {"title": "update BIGSELLER", "description": "Update data dan pastikan sinkron.", "quest_date": str(date.today()), "assigned_to": ["JEJEN"]},
    {"title": "sanggah pelanggaran", "description": "Ajukan sanggahan untuk pelanggaran yang valid.", "quest_date": str(date.today()), "assigned_to": ["OLA"]},
    {"title": "cek merek brand", "description": "Periksa status merek brand terbaru.", "quest_date": str(date.today()), "assigned_to": ["JUMIO"]},
    {"title": "cek badge", "description": "Cek badge dan catat histori naik/turun.", "quest_date": str(date.today()), "assigned_to": ["JEJEN", "OLA", "JUMIO"]},
    {"title": "cek rating", "description": "Cek rating dan catat histori naik/turun.", "quest_date": str(date.today()), "assigned_to": ["JEJEN", "OLA", "JUMIO"]},
    {"title": "cek violation", "description": "Cek violation dan catat histori naik/turun.", "quest_date": str(date.today()), "assigned_to": ["JEJEN", "OLA", "JUMIO"]},
]


def load_data() -> Dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    quests = []
    for idx, q in enumerate(DEFAULT_QUESTS, start=1):
        quests.append(
            {
                "id": idx,
                "title": q["title"],
                "description": q["description"],
                "quest_date": q["quest_date"],
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "created_by": "ADMIN",
                "assigned_to": q["assigned_to"],
                "status": {pic: "Belum dikerjakan" for pic in q["assigned_to"]},
                "proof_links": {pic: "" for pic in q["assigned_to"]},
                "completed_at": {pic: "" for pic in q["assigned_to"]},
            }
        )

    data = {
        "pics": [
            {"name": pic, "exp": 0, "level": 1, "completed_quests": 0}
            for pic in DEFAULT_PICS
        ],
        "quests": quests,
        "next_quest_id": len(quests) + 1,
    }
    save_data(data)
    return data



def save_data(data: Dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



def get_pic(data: Dict, name: str) -> Dict:
    for pic in data["pics"]:
        if pic["name"] == name:
            return pic
    raise ValueError(f"PIC tidak ditemukan: {name}")



def award_exp(pic: Dict, exp_gain: int = 100):
    current_total = max((pic["level"] - 1) * 100, 0) + pic["exp"]
    new_total = current_total + exp_gain
    pic["level"] = max(1, new_total // 100 + 1)
    pic["exp"] = new_total % 100
    pic["completed_quests"] += 1



def completion_percent(total: int, done: int) -> float:
    if total == 0:
        return 0.0
    return round((done / total) * 100, 1)



def build_performance_df(data: Dict) -> pd.DataFrame:
    rows: List[Dict] = []
    for pic in data["pics"]:
        assigned = 0
        done = 0
        pending_titles = []
        for quest in data["quests"]:
            if pic["name"] in quest["assigned_to"]:
                assigned += 1
                if quest["status"].get(pic["name"]) == "Selesai":
                    done += 1
                else:
                    pending_titles.append(quest["title"])
        rows.append(
            {
                "PIC": pic["name"],
                "Assigned Quest": assigned,
                "Selesai": done,
                "Belum Selesai": max(assigned - done, 0),
                "Completion %": completion_percent(assigned, done),
                "Level": pic["level"],
                "EXP Saat Ini": pic["exp"],
                "Daftar Pending": ", ".join(pending_titles) if pending_titles else "-",
            }
        )
    return pd.DataFrame(rows)



def get_notifications(data: Dict, pic_name: str = None) -> List[str]:
    notifications = []
    today = str(date.today())
    for quest in sorted(data["quests"], key=lambda x: x["quest_date"], reverse=True):
        targets = quest["assigned_to"]
        is_new = quest["quest_date"] >= today
        if pic_name:
            if pic_name not in targets:
                continue
            status = quest["status"].get(pic_name, "Belum dikerjakan")
            if is_new:
                notifications.append(f"Quest baru: {quest['title']}")
            if status != "Selesai":
                notifications.append(f"Belum dikerjakan: {quest['title']}")
        else:
            open_count = sum(1 for p in targets if quest["status"].get(p) != "Selesai")
            if is_new:
                notifications.append(f"Quest baru dibuat: {quest['title']}")
            if open_count > 0:
                notifications.append(f"{quest['title']} masih pending untuk {open_count} PIC")
    seen = set()
    unique = []
    for item in notifications:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique[:20]



def render_notifications(data: Dict, pic_name: str = None):
    st.subheader("Notifikasi Quest")
    notifications = get_notifications(data, pic_name)
    if not notifications:
        st.success("Tidak ada notifikasi. Semua aman.")
        return
    for note in notifications:
        st.info(note)



def admin_view(data: Dict):
    st.header("Panel Admin")
    render_notifications(data)

    st.subheader("Tambah Quest Baru")
    with st.form("add_quest_form", clear_on_submit=True):
        title = st.text_input("Judul Quest")
        description = st.text_area("Deskripsi Quest")
        quest_date = st.date_input("Tanggal Quest", value=date.today())
        selected_pics = st.multiselect("Assign ke PIC", DEFAULT_PICS, default=DEFAULT_PICS)
        submitted = st.form_submit_button("Tambah Quest")

        if submitted:
            if not title.strip() or not description.strip() or not selected_pics:
                st.error("Judul, deskripsi, dan PIC wajib diisi.")
            else:
                new_quest = {
                    "id": data["next_quest_id"],
                    "title": title.strip(),
                    "description": description.strip(),
                    "quest_date": str(quest_date),
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                    "created_by": "ADMIN",
                    "assigned_to": selected_pics,
                    "status": {pic: "Belum dikerjakan" for pic in selected_pics},
                    "proof_links": {pic: "" for pic in selected_pics},
                    "completed_at": {pic: "" for pic in selected_pics},
                }
                data["quests"].append(new_quest)
                data["next_quest_id"] += 1
                save_data(data)
                st.success("Quest berhasil ditambahkan.")
                st.rerun()

    st.subheader("Ringkasan Performa PIC")
    perf_df = build_performance_df(data)
    st.dataframe(perf_df, use_container_width=True)
    st.bar_chart(perf_df.set_index("PIC")[["Selesai", "Belum Selesai"]])

    st.subheader("Daftar Semua Quest")
    all_rows = []
    for quest in sorted(data["quests"], key=lambda x: (x["quest_date"], x["id"]), reverse=True):
        all_rows.append(
            {
                "ID": quest["id"],
                "Judul": quest["title"],
                "Deskripsi": quest["description"],
                "Tanggal Quest": quest["quest_date"],
                "Assigned": ", ".join(quest["assigned_to"]),
                "Status Ringkas": "; ".join([f"{k}: {v}" for k, v in quest["status"].items()]),
            }
        )
    st.dataframe(pd.DataFrame(all_rows), use_container_width=True)



def pic_view(data: Dict, pic_name: str):
    st.header(f"Dashboard PIC - {pic_name}")
    pic = get_pic(data, pic_name)

    c1, c2, c3 = st.columns(3)
    c1.metric("Level", pic["level"])
    c2.metric("EXP", f"{pic['exp']}/100")
    c3.metric("Quest Selesai", pic["completed_quests"])

    render_notifications(data, pic_name)

    st.subheader("Quest Saya")
    my_quests = [q for q in data["quests"] if pic_name in q["assigned_to"]]
    if not my_quests:
        st.warning("Belum ada quest untuk PIC ini.")
        return

    for quest in sorted(my_quests, key=lambda x: (x["quest_date"], x["id"]), reverse=True):
        status = quest["status"].get(pic_name, "Belum dikerjakan")
        with st.expander(f"[{status}] {quest['title']} - {quest['quest_date']}"):
            st.write(f"**Deskripsi:** {quest['description']}")
            st.write(f"**Status saat ini:** {status}")
            existing_proof = quest["proof_links"].get(pic_name, "")
            if existing_proof:
                st.markdown(f"**Proof:** [Lihat screenshot]({existing_proof})")
            new_status = st.selectbox(
                f"Update status #{quest['id']}",
                ["Belum dikerjakan", "Sedang dikerjakan", "Selesai"],
                index=["Belum dikerjakan", "Sedang dikerjakan", "Selesai"].index(status),
                key=f"status_{quest['id']}_{pic_name}",
            )
            proof_link = st.text_input(
                f"Link screenshot proof #{quest['id']}",
                value=existing_proof,
                key=f"proof_{quest['id']}_{pic_name}",
                placeholder="https://...",
            )
            if st.button("Simpan Update", key=f"save_{quest['id']}_{pic_name}"):
                prev_status = quest["status"].get(pic_name, "Belum dikerjakan")
                if new_status == "Selesai" and not proof_link.strip():
                    st.error("Untuk menyelesaikan quest, link screenshot proof wajib diisi.")
                else:
                    quest["status"][pic_name] = new_status
                    quest["proof_links"][pic_name] = proof_link.strip()
                    if new_status == "Selesai" and prev_status != "Selesai":
                        quest["completed_at"][pic_name] = datetime.now().isoformat(timespec="seconds")
                        award_exp(pic, 100)
                        st.success("Quest selesai. Kamu dapat +100 EXP / naik 1 level tiap 100 EXP.")
                    elif new_status != "Selesai":
                        quest["completed_at"][pic_name] = ""
                    save_data(data)
                    st.rerun()

    st.subheader("Performa Saya")
    assigned = len(my_quests)
    done = sum(1 for q in my_quests if q["status"].get(pic_name) == "Selesai")
    pending = assigned - done
    perf = pd.DataFrame(
        {
            "Status": ["Selesai", "Belum Selesai"],
            "Jumlah": [done, pending],
        }
    )
    st.dataframe(
        pd.DataFrame(
            [{
                "Assigned Quest": assigned,
                "Selesai": done,
                "Belum Selesai": pending,
                "Completion %": completion_percent(assigned, done),
                "Level": pic["level"],
                "EXP": pic["exp"],
            }]
        ),
        use_container_width=True,
    )
    st.bar_chart(perf.set_index("Status"))



def main():
    st.set_page_config(page_title=APP_NAME, page_icon="📌", layout="wide")
    st.title(APP_NAME)
    st.caption("Dashboard tugas dengan sistem quest, notifikasi, proof screenshot, dan performa PIC.")

    data = load_data()

    with st.sidebar:
        st.header("Akses")
        role = st.radio("Pilih role", ["Admin", "PIC"], horizontal=False)
        if role == "Admin":
            password = st.text_input("Password Admin", type="password")
            if password != ADMIN_PASSWORD:
                st.warning("Masukkan password admin untuk membuka panel.")
                st.info("Password default: admin123")
                return
            admin_view(data)
        else:
            pic_name = st.selectbox("Pilih PIC", DEFAULT_PICS)
            pic_view(data, pic_name)

    st.sidebar.markdown("---")
    st.sidebar.write("**PIC aktif:**")
    for pic in DEFAULT_PICS:
        st.sidebar.write(f"- {pic}")


if __name__ == "__main__":
    main()
