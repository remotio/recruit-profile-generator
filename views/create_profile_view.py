import streamlit as st
import datetime
import time

JAPANESE_UNIVERSITIES = [
    "東京大学", "京都大学", "大阪大学", "東北大学", "名古屋大学",
    "九州大学", "北海道大学", "東京工業大学", "一橋大学", "神戸大学",
    "早稲田大学", "慶應義塾大学", "上智大学", "東京理科大学",
    "明治大学", "青山学院大学", "立教大学", "中央大学", "法政大学",
    "同志社大学", "立命館大学", "関西大学", "関西学院大学",
    "福岡大学"
]
PREFECTURES = [
    "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
    "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
    "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
    "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
    "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
    "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
    "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
]
DEPARTMENTS = [
    "法学部", "経済学部", "経営学部", "商学部", "文学部", "人文学部",
    "社会学部", "国際関係学部", "外国語学部", "教育学部", "理学部",
    "工学部", "情報理工学部", "農学部", "医学部", "歯学部", "薬学部",
    "芸術学部", "体育学部", "総合政策学部", "環境情報学部"
]

def render_page():
    """「プロフィール作成」ページを描画する関数"""
    
    # このコードはダミーのmanagerオブジェクトを使用しています。
    # 実際のアプリケーションでは、適切なmanagerをインスタンス化してください。
    class DummyProfileManager:
        def upload_profile_image(self, user_id, file_body, file_name):
            print(f"Uploading {file_name} for user {user_id}...")
            return f"https://example.com/images/{user_id}/{file_name}"
        def create_profile(self, profile_data):
            print("Creating profile:", profile_data)
            return True
        def check_profile_exists(self, user_id):
            print(f"Checking if profile exists for user {user_id}...")
            return True

    if 'profile_manager' not in st.session_state:
        st.session_state.profile_manager = DummyProfileManager()
    if 'user' not in st.session_state:
        st.session_state.user = {'id': 'test_user_123'}

    manager = st.session_state.profile_manager
    
    if 'hobbies' not in st.session_state:
        st.session_state.hobbies = [""]
    
    def add_hobby():
        st.session_state.hobbies.append("")
    def delete_hobby(index):
        if len(st.session_state.hobbies) > 1:
            st.session_state.hobbies.pop(index)

    st.subheader("新しいプロフィールを作成", divider="blue")

    st.write("あなたのことを教えてください（*は必須項目です）")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("姓 *", key="last_name")
        st.text_input("ニックネーム *", key="nickname")
        st.selectbox("大学名 *", JAPANESE_UNIVERSITIES, index=None, placeholder="大学名を選択または入力して検索...", key="university")
        st.selectbox("出身地 *", PREFECTURES, index=None, placeholder="都道府県を選択または入力して検索...", key="hometown")
    with col2:
        st.text_input("名 *", key="first_name")
        st.date_input("誕生日 *", min_value=datetime.date(1980, 1, 1), max_value=datetime.date(2010, 12, 31), value=None, key="birth_date")
        st.selectbox("学部 *", DEPARTMENTS, index=None, placeholder="学部・学科を選択または入力して検索...", key="department")
    
    st.divider()
    
    st.subheader("プロフィール画像")
    uploaded_file = st.file_uploader(
        "画像をアップロード", 
        type=["png", "jpg", "jpeg"], 
        key="profile_image_uploader"
    )
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption='アップロードされた画像', use_column_width=False, width=150)
    
    st.divider()

    st.subheader("趣味")
    for i in range(len(st.session_state.hobbies)):
        input_col, delete_col = st.columns([4, 1])
        with input_col:
            st.session_state.hobbies[i] = st.text_input(f"{i + 1}つ目", value=st.session_state.hobbies[i], key=f"hobby_{i}", label_visibility="collapsed")
        with delete_col:
            st.button("削除", key=f"delete_hobby_{i}", on_click=delete_hobby, args=(i,), use_container_width=True)
    st.button("＋追加", on_click=add_hobby, key="add_hobby")

    st.divider()

    st.text_area("話すと嬉しくなること", placeholder="例: おすすめの映画について話したいです！", key="happy_topic")
    st.text_area("ちょっと詳しいこと", placeholder="例: 美味しいコーヒーの淹れ方には自信があります", key="expert_topic")
    st.write("")
    
    # タグ入力のUIを削除
    if 'tags' in st.session_state:
        del st.session_state.tags
        
    if st.button("自己紹介を自動生成する！", use_container_width=True, type="primary"):
        # 必須項目がすべて入力・選択されているかチェック
        if not (st.session_state.last_name and
                st.session_state.first_name and
                st.session_state.nickname and
                st.session_state.birth_date and
                st.session_state.university and
                st.session_state.department and
                st.session_state.hometown):
            st.error("「*」が付いている項目はすべて選択・入力してください。")
        else:
            with st.spinner("AIがあなたの自己紹介を生成中です..."):
                hobbies = [h for h in st.session_state.hobbies if h]
                
                profile_data = {
                    "id": st.session_state.user['id'], 
                    "last_name": st.session_state.last_name, 
                    "first_name": st.session_state.first_name,
                    "nickname": st.session_state.nickname, 
                    "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d") if st.session_state.birth_date else None,
                    "university": st.session_state.university,
                    "department": st.session_state.department, 
                    "hometown": st.session_state.hometown,
                    "hobbies": hobbies,
                    "happy_topic": st.session_state.happy_topic, 
                    "expert_topic": st.session_state.expert_topic,
                }
                
                # プロフィール画像のアップロード
                if uploaded_file is not None:
                    try:
                        file_bytes = uploaded_file.getvalue()
                        public_url = manager.upload_profile_image(
                            user_id=st.session_state.user['id'],
                            file_body=file_bytes,
                            file_name=uploaded_file.name
                        )
                        profile_data["profile_image_url"] = public_url
                        st.toast("画像をアップロードしました！", icon="🎉")

                    except Exception as e:
                        st.error(f"画像のアップロードに失敗しました: {e}")
                        return
                
                response = manager.create_profile(profile_data)

            if response:
                st.success("プロフィールを作成しました！マイページに移動します。")
                
                with st.spinner("データベースを同期中..."):
                    profile_found = False
                    for _ in range(5):
                        if manager.check_profile_exists(st.session_state.user['id']):
                            profile_found = True
                            break
                        time.sleep(1)
                    
                if profile_found:
                    st.session_state.profile_exists = True
                    st.session_state.active_page = "マイページ"
                    st.rerun()
                else:
                    st.error("プロフィールの同期に失敗しました。時間をおいて再度お試しください。")
            else:
                st.error("自己紹介の生成に失敗しました。")
