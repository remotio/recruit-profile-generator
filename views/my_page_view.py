import streamlit as st
import datetime
from .profile_detail_component import display_profile_detail
import streamlit as st
import qrcode
from io import BytesIO


def render_page():
    """
    マイページを描画する関数。
    ログイン中のユーザーのプロフィールを常に表示・編集する。
    """
    
    manager = st.session_state.profile_manager
    current_login_user_id = st.session_state.user['id']
    
    st.subheader("マイページ", divider="blue")

    try:
        current_user_profile = manager.get_profile_by_id(current_login_user_id)
    except Exception as e:
        st.error(f"プロフィールの読み込み中にエラーが発生しました: {e}")
        st.warning("まだプロフィールが作成されていない可能性があります。「プロフィール作成」ページから作成してください。")
        st.stop()

    if not current_user_profile:
        st.warning("あなたのプロフィールが見つかりません。「プロフィール作成」ページからご自身のプロフィールを作成してください。")
        st.stop()

    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False


    # (1) 表示モード
    if not st.session_state.edit_mode:
        if 'edit_hobbies' in st.session_state:
            del st.session_state.edit_hobbies
        if 'edit_tags' in st.session_state:
            del st.session_state.edit_tags

        display_profile_detail(current_user_profile) 

        if st.button("プロフィールを編集する", type="primary"):
            st.session_state.edit_mode = True
            st.rerun()
        
        # QR関連
        if 'show_qr' not in st.session_state:
            st.session_state.show_qr = False
        def toggle_qr():
            st.session_state.show_qr = not st.session_state.show_qr
        st.button("プロフィールQRコードを表示/非表示", on_click=toggle_qr)
        # state.show_qrがtrueの場合のみQRコードを表示
        if st.session_state.show_qr:
            with st.container(border=True):
                current_user_id=st.session_state.user['id']
                BASE_URL="https://recruit-profile-gen.streamlit.app"
                # QRコードに含めるURLを生成
                my_profile_url = f"{BASE_URL}/?page=profile_detail&id={current_login_user_id}"

                # QRコードを画像としてメモリ上に生成
                img = qrcode.make(my_profile_url)
                buf = BytesIO()
                img.save(buf, format="PNG")
                img_bytes = buf.getvalue()

                # QRコードを表示
                st.image(img_bytes, width=200)
                st.code(my_profile_url, language="text")
                st.caption("このQRコードを使って，あなたのプロフィールを簡単に共有できます！")
        

    # (2) 編集モード
    else:
        if 'edit_hobbies' not in st.session_state:
            hobbies_from_top_level = current_user_profile.get("hobbies", [])
            if hobbies_from_top_level:
                 st.session_state.edit_hobbies = hobbies_from_top_level or [""]
            else:
                talk_topics = current_user_profile.get("generated_profile", {}).get("talk_topics", {})
                hobbies_str = talk_topics.get("hobbies", "")
                st.session_state.edit_hobbies = [h.strip() for h in hobbies_str.split(',') if h.strip()] or [""]

        if 'edit_tags' not in st.session_state:
            raw_tags = current_user_profile.get("tags", [])
            st.session_state.edit_tags = [tag.lstrip('#').strip() for tag in raw_tags] or [""]

        def add_hobby():
            st.session_state.edit_hobbies.append("")
        def delete_hobby(index):
            if len(st.session_state.edit_hobbies) > 1:
                st.session_state.edit_hobbies.pop(index)
        def add_tag():
            st.session_state.edit_tags.append("")
        def delete_tag(index):
            if len(st.session_state.edit_tags) > 1:
                st.session_state.edit_tags.pop(index)

        st.info("情報を編集して、保存ボタンを押してください。")

        gen_profile = current_user_profile.get("generated_profile", {})
        basic_info = gen_profile.get("basic_info", {})
        talk_topics = gen_profile.get("talk_topics", {})
        animal_result = current_user_profile.get("animal_result", {})

        JAPANESE_UNIVERSITIES = [ "東京大学", "京都大学", "大阪大学", "東北大学", "名古屋大学", "九州大学", "北海道大学", "東京工業大学", "一橋大学", "神戸大学", "早稲田大学", "慶應義塾大学", "上智大学", "東京理科大学", "明治大学", "青山学院大学", "立教大学", "中央大学", "法政大学", "同志社大学", "立命館大学", "関西大学", "関西学院大学", "福岡大学" ]
        PREFECTURES = [ "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県" ]
        DEPARTMENTS = [ "法学部", "経済学部", "経営学部", "商学部", "文学部", "人文学部", "社会学部", "国際関係学部", "外国語学部", "教育学部", "理学部", "工学部", "情報理工学部", "農学部", "医学部", "歯学部", "薬学部", "芸術学部", "体育学部", "総合政策学部", "環境情報学部" ]

        tab1, tab2, tab3 = st.tabs(["基本情報", "詳細情報", "その他"])

        with tab1:
            st.subheader("基本情報")
            col1, col2 = st.columns(2)
            with col1:
                last_name_val = basic_info.get("last_name") or current_user_profile.get("last_name", "")
                last_name = st.text_input("姓", value=last_name_val, key="last_name")
                
                nickname = st.text_input("ニックネーム *", value=current_user_profile.get("nickname", ""), key="nickname")

                current_university = basic_info.get("university") or current_user_profile.get("university")
                university_index = JAPANESE_UNIVERSITIES.index(current_university) if current_university in JAPANESE_UNIVERSITIES else None
                university = st.selectbox("大学名 *", JAPANESE_UNIVERSITIES, index=university_index, placeholder="大学を選択してください", key="university")
            with col2:
                first_name_val = basic_info.get("first_name") or current_user_profile.get("first_name", "")
                first_name = st.text_input("名", value=first_name_val, key="first_name")
                
                birth_date_val = basic_info.get("birth_date") or current_user_profile.get("birth_date")
                birth_date_obj = datetime.datetime.strptime(birth_date_val, "%Y-%m-%d").date() if birth_date_val else None
                birth_date = st.date_input("生年月日", value=birth_date_obj, key="birth_date")
                
                current_department = basic_info.get("department") or current_user_profile.get("department")
                department_index = DEPARTMENTS.index(current_department) if current_department in DEPARTMENTS else None
                department = st.selectbox("学部 *", DEPARTMENTS, index=department_index, placeholder="学部を選択してください", key="department")
            
            current_hometown = basic_info.get("hometown") or current_user_profile.get("hometown")
            hometown_index = PREFECTURES.index(current_hometown) if current_hometown in PREFECTURES else None
            hometown = st.selectbox("出身地", PREFECTURES, index=hometown_index, placeholder="都道府県を選択してください", key="hometown")

        with tab2:
            st.subheader("趣味")
            for i, hobby in enumerate(st.session_state.edit_hobbies):
                input_col, delete_col = st.columns([4, 1])
                with input_col:
                    st.session_state.edit_hobbies[i] = st.text_input(f"hobby_{i}", value=hobby, key=f"edit_hobby_{i}", label_visibility="collapsed")
                with delete_col:
                    st.button("削除", key=f"delete_hobby_{i}", on_click=delete_hobby, args=(i,), use_container_width=True)
            st.button("＋追加", on_click=add_hobby, key="add_hobby_btn")
            st.markdown("---")
            st.subheader("タグ")
            for i, tag in enumerate(st.session_state.edit_tags):
                input_col, delete_col = st.columns([4, 1])
                with input_col:
                    st.session_state.edit_tags[i] = st.text_input(f"tag_{i}", value=tag, key=f"edit_tag_{i}", label_visibility="collapsed", placeholder="例: カフェ好き")
                with delete_col:
                    st.button("削除", key=f"delete_tag_{i}", on_click=delete_tag, args=(i,), use_container_width=True)
            st.button("＋追加", on_click=add_tag, key="add_tag_btn")
            st.markdown("---")
            happy_topic_val = talk_topics.get("happy_topic") or current_user_profile.get("happy_topic", "")
            happy_topic = st.text_area("みんなと話したいこと", value=happy_topic_val, key="happy_topic")
            
            expert_topic_val = talk_topics.get("expert_topic") or current_user_profile.get("expert_topic", "")
            expert_topic = st.text_area("ちょっと詳しいこと", value=expert_topic_val, key="expert_topic")

        with tab3:
            st.subheader("画像とキャラクター")
            profile_image_url = st.text_input("プロフィール画像URL", value=current_user_profile.get("profile_image_url", ""), key="profile_image_url")
            animal_image_url = st.text_input("動物アバター画像URL", value=current_user_profile.get("animal_image_url", ""), key="animal_image_url")
            st.markdown("---")
            animal_name_val = animal_result.get("name") or current_user_profile.get("animal_name", "")
            animal_name = st.text_input("動物名", value=animal_name_val, key="animal_name")

            animal_reason_val = animal_result.get("reason") or current_user_profile.get("animal_reason", "")
            animal_reason = st.text_area("その動物である理由", value=animal_reason_val, key="animal_reason")

        st.markdown("---")
        
        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("変更を保存する", use_container_width=True, type="primary"):
                with st.spinner("プロフィールを更新しています..."):
                    hobbies_list = [h.strip() for h in st.session_state.edit_hobbies if h.strip()]
                    tags_list = [t.strip() for t in st.session_state.edit_tags if t.strip()]
                    
                    updated_data = {
                        "id": current_login_user_id,
                        "last_name": st.session_state.last_name, "first_name": st.session_state.first_name, 
                        "nickname": st.session_state.nickname,
                        "university": st.session_state.university, 
                        "department": st.session_state.department, 
                        "hometown": st.session_state.hometown,
                        "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d") if st.session_state.birth_date else "",
                        "hobbies": hobbies_list, "tags": tags_list,
                        "happy_topic": st.session_state.happy_topic, "expert_topic": st.session_state.expert_topic,
                    }
                    manager.update_user_input(current_login_user_id, updated_data)

                st.success("プロフィールが更新されました！")
                st.session_state.edit_mode = False
                st.rerun()
        
        with col_cancel:
            if st.button("キャンセル", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()

