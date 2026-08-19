import streamlit as st
import requests
import json
from datetime import datetime
import urllib.parse

# 1. アプリの裏側の設定
st.set_page_config(page_title="向洋大原自治会", page_icon="🏡", layout="centered")

# ★ご自身のGASのURLが入っているか確認してください
GAS_URL = "https://script.google.com/macros/s/AKfycby4K-p_AZRlbpK85WijSwqjkUN8DtR9ExrG-WHrZhQP8qPqxvJ20sOkewWqf4Wu9TabiA/exec"

# ★実際のアプリURLを入力してください
APP_URL = "https://jichikai-app-grtxv8oupmdqtfkddsuhmn.streamlit.app/"  

def fetch_data():
    """スプレッドシートからお知らせとカレンダー情報を安全に取得する関数"""
    if "★" in GAS_URL or not GAS_URL:
        return {"notices": [], "events": []}
    try:
        res = requests.get(GAS_URL)
        res_data = res.json()
        
        # 以前の旧GAS（配列形式）と新GAS（辞書形式）の両方に対応する処理
        if isinstance(res_data, list):
            return {"notices": res_data, "events": []}
        elif isinstance(res_data, dict):
            return {
                "notices": res_data.get("notices", []),
                "events": res_data.get("events", [])
            }
        return {"notices": [], "events": []}
    except Exception as e:
        return {"notices": [], "events": []}

def send_to_gas(payload):
    """GASにデータ（既読・SOS）を送信する関数"""
    if "★" in GAS_URL or not GAS_URL:
        st.warning("⚠️ GASのURLが設定されていません。")
        return False
    try:
        res = requests.post(GAS_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        return res.json().get("result") == "success"
    except Exception as e:
        st.error(f"送信エラー: {e}")
        return False

st.title("🏡 向洋大原自治会アプリ")

# --- サイドバー：会員情報設定エリア ---
st.sidebar.header("🪪 会員情報設定")
user_name = st.sidebar.text_input("お名前", value="大原 太郎")
user_ban = st.sidebar.selectbox("所属する班", ["1班", "2班", "3班", "4班", "5班"])
user_role = st.sidebar.selectbox("役職区分", ["一般会員", "現役役員", "役員経験者(OB/OG)"])
user_id = st.sidebar.text_input("会員ID（または電話番号）", value="OHARA-0001")

# カードデザイン設定
if user_role == "現役役員":
    card_bg = "linear-gradient(135deg, #BF953F 0%, #FCF6BA 25%, #B38728 50%, #FBF5B7 75%, #AA771C 100%)"
    card_text_color = "#333333"
    role_badge = "🌟 現役役員"
elif user_role == "役員経験者(OB/OG)":
    card_bg = "linear-gradient(135deg, #134E5E 0%, #71B280 100%)"
    card_text_color = "#ffffff"
    role_badge = "🎖️ 役員経験者(OB/OG)"
else:
    card_bg = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)"
    card_text_color = "#ffffff"
    role_badge = "🏡 一般会員"

# データ安全取得
data = fetch_data()
notices = data.get("notices", [])
events = data.get("events", [])

# --- メイン機能 ---
tab_card, tab_notice, tab_cal, tab_sos = st.tabs(["🪪 会員証", "📢 お知らせ", "📅 カレンダー", "🆘 安否確認"])

# --- 1. 会員証 ---
with tab_card:
    st.subheader("🪪 向洋大原自治会 デジタル会員証")
    st.markdown(f"""
    <div style="background: {card_bg}; color: {card_text_color}; padding: 20px; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.9rem; opacity: 0.9;">向洋大原自治会 公式会員証</span>
            <span style="font-size: 0.85rem; font-weight: bold; background: rgba(0,0,0,0.15); padding: 3px 8px; border-radius: 10px;">{role_badge}</span>
        </div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 15px 0 5px 0;">{user_name} 様</div>
        <hr style="border: 0.5px solid rgba(255,255,255,0.4);">
        <div style="display: flex; justify-content: space-between; font-size: 1rem;">
            <span>所属: <b>{user_ban}</b></span>
            <span>ID: <b>{user_id}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.success(f"✅ 有効な会員証です（区分: {user_role}）。")

# --- 2. お知らせ ---
with tab_notice:
    st.subheader("📢 回覧板・お知らせ")
    st.caption(f"👤 現在の確認者: {user_name} 様 ({user_ban} / {user_role})")
    
    if st.button("🔄 お知らせを再読み込み"):
        st.rerun()

    if not notices or not isinstance(notices, list):
        st.info("現在、新しいお知らせはありません。（または読み込み中...）")
    else:
        today = datetime.now()
        
        for idx, notice in enumerate(notices):
            if not isinstance(notice, dict):
                continue
                
            is_new = False
            raw_date = str(notice.get('date', ''))
            display_date = raw_date
            
            if raw_date:
                try:
                    clean_date = raw_date.split("T")[0].replace("-", "/")
                    post_date = datetime.strptime(clean_date, "%Y/%m/%d")
                    display_date = post_date.strftime("%Y年%m月%d日")
                    if (today - post_date).days <= 7:
                        is_new = True
                except:
                    pass
            
            if idx == 0:
                is_new = True

            title_val = notice.get('title', '無題')
            title_display = f"🚨【NEW! 新着】{title_val}" if is_new else title_val
            is_first = (idx == 0)
            
            with st.expander(title_display, expanded=is_first):
                if is_new:
                    st.markdown("""
                    <div style="background-color: #FFF3CD; border-left: 6px solid #FF8C00; color: #856404; padding: 10px 15px; border-radius: 5px; font-weight: bold; margin-bottom: 12px;">
                        🔥 🔴【新着のお知らせ】必ずご確認ください！
                    </div>
                    """, unsafe_allow_html=True)
                
                st.write(f"**投稿日:** {display_date}")
                st.write(notice.get('content', ''))
                
                file_url = notice.get('fileUrl', '')
                if file_url:
                    st.markdown(f"""
                    <a href="{file_url}" target="_blank" style="text-decoration: none;">
                        <div style="background-color: #e7f5ff; border: 1px solid #74c0fc; color: #1864ab; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin: 10px 0;">
                            📄 添付資料（ポスター・PDF）を開く ↗️
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                btn_key = f"read_btn_{notice.get('id', idx)}"
                if st.button("✅ 読みました（送信）", key=btn_key):
                    with st.spinner("送信中..."):
                        payload = {
                            "type": "notice",
                            "userName": user_name,
                            "userBan": user_ban,
                            "userRole": user_role,
                            "title": title_val
                        }
                        if send_to_gas(payload):
                            st.success(f"🎉 スプレッドシートへ記録されました！（送信者: {user_name} 様）")

                line_text = f"【向洋大原自治会からのお知らせ】\n\n📌 {title_val}\n\n{notice.get('content', '')}\n\n👇 詳細確認・「読みました」送信はこちらから\n{APP_URL}"
                encoded_text = urllib.parse.quote(line_text)
                line_share_url = f"https://line.me/R/msg/text/?{encoded_text}"
                
                st.markdown(f"""
                <a href="{line_share_url}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #06C755; color: white; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        💬 このお知らせをLINEで住民へ送信・通知する ↗️
                    </div>
                </a>
                """, unsafe_allow_html=True)

# --- 3. カレンダー ---
with tab_cal:
    st.subheader("📅 地域合同 行事カレンダー")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1: show_jichikai = st.checkbox("自治会", value=True)
    with col_f2: show_kodomo = st.checkbox("子ども会", value=True)
    with col_f3: show_salon = st.checkbox("いきいきサロン", value=True)
    with col_f4: show_taikyo = st.checkbox("体育協会", value=True)
    st.divider()
    
    style_map = {
        "自治会": {"bg": "#FFF3CD", "text": "#856404"},
        "子ども会": {"bg": "#D1ECF1", "text": "#0C5460"},
        "いきいきサロン": {"bg": "#D4EDDA", "text": "#155724"},
        "体育協会": {"bg": "#F8D7DA", "text": "#721C24"}
    }
    
    if not events or not isinstance(events, list):
        st.info("現在、予定されている行事はありません。")
    else:
        for ev in events:
            if not isinstance(ev, dict):
                continue
            org = ev.get("org", "自治会")
            if (org == "自治会" and show_jichikai) or (org == "子ども会" and show_kodomo) or (org == "いきいきサロン" and show_salon) or (org == "体育協会" and show_taikyo):
                st_style = style_map.get(org, {"bg": "#E2E3E5", "text": "#383D41"})
                st.markdown(f"""<div style="background-color: {st_style['bg']}; color: {st_style['text']}; padding: 12px 15px; border-radius: 10px; margin-bottom: 12px; border-left: 6px solid {st_style['text']};">
                    <div style="font-size: 0.85rem; font-weight: bold; opacity: 0.8;">【{org}】{ev.get('date', '')}</div>
                    <div style="font-size: 1.1rem; font-weight: bold; margin: 4px 0;">{ev.get('title', '')}</div>
                    <div style="font-size: 0.9rem; opacity: 0.9;">{ev.get('desc', '')}</div></div>""", unsafe_allow_html=True)

# --- 4. 防災・安否確認 ---
with tab_sos:
    st.subheader("🆘 災害時 安否確認・ご近所SOS")
    st.warning("⚠️ 地震や豪雨などの災害発生時のみ使用してください。自治会対策本部へ即座に状況が届きます。")
    st.caption(f"👤 送信者: {user_name} 様（{user_ban}）")
    sos_msg = st.text_input("現在の状況・一言メモ（任意）", placeholder="例：家族全員無事です / 1階が浸水しています など")
    col_sos1, col_sos2 = st.columns(2)
    with col_sos1:
        if st.button("🟢 全員無事です", use_container_width=True, key="btn_safe"):
            with st.spinner("安否報告を送信中..."):
                payload = {"type": "sos", "userName": user_name, "userBan": user_ban, "status": "無事", "message": sos_msg or "特記事項なし"}
                if send_to_gas(payload):
                    st.balloons()
                    st.success(f"【報告完了】{user_name} 様の「全員無事」を本部に報告しました！")
    with col_sos2:
        if st.button("🔴 助けが必要です（SOS）", use_container_width=True, key="btn_sos"):
            with st.spinner("緊急SOSを送信中..."):
                payload = {"type": "sos", "userName": user_name, "userBan": user_ban, "status": "🆘 救助・支援要請", "message": sos_msg or "緊急SOS"}
                if send_to_gas(payload):
                    st.error(f"🚨【SOS送信完了】{user_name} 様（{user_ban}）からの要請を本部・近隣へ送信しました！")
