import streamlit as st
import requests
import json
from datetime import datetime
import urllib.parse

# 1. アプリの裏側の設定
st.set_page_config(page_title="向洋大原自治会", page_icon="🏡", layout="centered")

# ★ご自身のGASのURLが入っているか確認してください
GAS_URL = "ここにコピーしたGASのURLを貼り付け"

# ★実際のアプリURLを入力してください
APP_URL = "https://jichikai-app-grtxv8oupmdqtfkddsuhmn.streamlit.app/"  

def fetch_data():
    """スプレッドシートから全データを取得する関数"""
    if "★" in GAS_URL or not GAS_URL:
        return {"notices": [], "events": [], "members": []}
    try:
        res = requests.get(GAS_URL)
        res_data = res.json()
        if isinstance(res_data, dict):
            return {
                "notices": res_data.get("notices", []),
                "events": res_data.get("events", []),
                "members": res_data.get("members", [])
            }
        return {"notices": [], "events": [], "members": []}
    except Exception as e:
        return {"notices": [], "events": [], "members": []}

def send_to_gas(payload):
    """GASにデータを送信する関数"""
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

# データ取得
data = fetch_data()
notices = data.get("notices", [])
events = data.get("events", [])
members = data.get("members", [])

# --- サイドバー：会員情報設定エリア（スプレッドシートの選択肢に完全準拠！） ---
st.sidebar.header("🪪 会員情報設定")
user_name = st.sidebar.text_input("お名前", value="大原 太郎")
user_ban = st.sidebar.selectbox("所属する班", ["1班", "2班", "3班", "4班", "5班"])

# D列（役職）の選択肢
user_role = st.sidebar.selectbox(
    "役職", 
    [
        "一般会員", 
        "自治会 会長", 
        "自治会 副会長", 
        "会計", 
        "監査", 
        "総務", 
        "書記", 
        "子ども会 会長", 
        "子ども会 副会長", 
        "福祉", 
        "民生", 
        "体協", 
        "評議員", 
        "班長"
    ]
)

# E列（役職2）の選択肢
user_role2 = st.sidebar.selectbox("役職2", ["設定なし", "夏フェス運営"])

user_id = st.sidebar.text_input("会員ID（または電話番号）", value="OHARA-0001")

# 名簿データ、またはサイドバーの選択値から「夏フェス運営」かどうかを判定
is_fes_staff = False

# 1. 手動選択（サイドバー）での判定
if user_role2 == "夏フェス運営":
    is_fes_staff = True

# 2. スプレッドシート名簿との突合による判定
matched_member = next((m for m in members if m.get("name") == user_name), None)
if matched_member and "夏フェス運営" in str(matched_member.get("role2", "")):
    is_fes_staff = True

# 会員証デザイン設定（役職に応じて豪華に変化）
officer_roles = ["自治会 会長", "自治会 副会長", "会計", "監査", "総務", "書記", "子ども会 会長", "子ども会 副会長"]

if user_role in officer_roles:
    card_bg = "linear-gradient(135deg, #BF953F 0%, #FCF6BA 25%, #B38728 50%, #FBF5B7 75%, #AA771C 100%)"
    card_text_color = "#333333"
    role_badge = f"🌟 {user_role}"
elif user_role != "一般会員":
    card_bg = "linear-gradient(135deg, #134E5E 0%, #71B280 100%)"
    card_text_color = "#ffffff"
    role_badge = f"🎖️ {user_role}"
else:
    card_bg = "linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)"
    card_text_color = "#ffffff"
    role_badge = "🏡 一般会員"

if user_role2 != "設定なし":
    role_badge += f" | 🎪 {user_role2}"

# --- メイン機能 ---
tab_card, tab_notice, tab_cal, tab_fes, tab_sos = st.tabs(["🪪 会員証", "📢 お知らせ", "📅 カレンダー", "🎪 夏フェス会計", "🆘 安否確認"])

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
    st.success(f"✅ 有効な会員証です（役職: {user_role} / 役職2: {user_role2}）。")

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
                            "userRole": f"{user_role}({user_role2})",
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

# --- 4. 夏フェス会計 ---
with tab_fes:
    st.subheader("🎪 夏フェス 収支記帳（運営関係者専用）")
    
    if not is_fes_staff:
        st.error("🔒 閲覧権限がありません")
        st.info("このエリアは、スプレッドシートの会員名簿で【役職2：夏フェス運営】となっているか、左メニューの【役職2】で「夏フェス運営」を選択している方のみ利用可能です。")
        st.caption(f"現在の設定: **{user_name}** 様（役職: {user_role} / 役職2: {user_role2}）")
    else:
        st.success(f"🔓 運営スタッフ確認完了（{user_name} 様）")
        st.divider()
        
        fes_mode = st.radio("入力項目を選択してください", ["💰 収入（協賛金・売上など）", "💸 支出（買い出し・経費など）"], horizontal=True)
        st.divider()
        
        if "💰 収入" in fes_mode:
            st.markdown("##### 💰 収入の記帳（協賛金・寄付金・売上）")
            inc_date = st.date_input("入金日", datetime.now())
            inc_cat = st.selectbox("区分", ["企業協賛金", "個人寄付", "出店・バザー売上", "自治会助成金", "その他"])
            inc_provider = st.text_input("提供者・企業名", placeholder="例：〇〇建設、山田太郎")
            inc_amount = st.number_input("金額（円）", min_value=0, step=1000, value=10000)
            inc_receipt = st.selectbox("領収書発行", ["発行済", "不要", "後日発行"])
            inc_memo = st.text_input("備考（リターン内容等）", placeholder="例：プログラム名刺広告掲載、提灯名入れなど")
            
            if st.button("💰 収入データを送信・記帳する", use_container_width=True):
                if not inc_provider:
                    st.error("提供者・企業名を入力してください。")
                else:
                    with st.spinner("送信中..."):
                        payload = {
                            "type": "fes_income",
                            "date": inc_date.strftime("%Y/%m/%d"),
                            "category": inc_cat,
                            "provider": inc_provider,
                            "amount": inc_amount,
                            "receipt": inc_receipt,
                            "memo": inc_memo
                        }
                        if send_to_gas(payload):
                            st.balloons()
                            st.success(f"🎉 『{inc_provider} 様』の収入データ（{inc_amount:,}円）を記帳しました！")

        else:
            st.markdown("##### 💸 支出の記帳（経費・買い出し）")
            exp_date = st.date_input("購入・支払日", datetime.now())
            exp_dept = st.selectbox("担当部門", ["自治会", "子ども会", "合同実行委員会"])
            exp_payee = st.text_input("支払先（店名等）", placeholder="例：〇〇スーパー、ダイソー、〇〇酒屋")
            exp_item = st.text_input("品名・用途", placeholder="例：かき氷シロップ、装飾用テープ、花火代")
            exp_amount = st.number_input("金額（円）", min_value=0, step=100, value=1500)
            exp_memo = st.text_input("備考", placeholder="例：レシート保管済、領収書No.123 など")
            
            if st.button("💸 支出データを送信・記帳する", use_container_width=True):
                if not exp_payee or not exp_item:
                    st.error("支払先と品名・用途を入力してください。")
                else:
                    with st.spinner("送信中..."):
                        payload = {
                            "type": "fes_expense",
                            "date": exp_date.strftime("%Y/%m/%d"),
                            "department": exp_dept,
                            "payee": exp_payee,
                            "item": exp_item,
                            "amount": exp_amount,
                            "memo": exp_memo
                        }
                        if send_to_gas(payload):
                            st.success(f"✅ 『{exp_payee}（{exp_item}）』の支出データ（{exp_amount:,}円）を記帳しました！")

# --- 5. 防災・安否確認 ---
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
