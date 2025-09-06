import streamlit as st
import datetime

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
    
    manager = st.session_state.profile_manager
    
    if 'hobbies' not in st.session_state:
        st.session_state.hobbies = [""]
    if 'tags' not in st.session_state:
        st.session_state.tags = [""]

    def add_hobby():
        st.session_state.hobbies.append("")
    def delete_hobby(index):
        if len(st.session_state.hobbies) > 1:
            st.session_state.hobbies.pop(index)
    def add_tag():
        st.session_state.tags.append("")
    def delete_tag(index):
        if len(st.session_state.tags) > 1:
            st.session_state.tags.pop(index)

    st.subheader("新しいプロフィールを作成", divider="blue")

    st.write("あなたのことを教えてください（*は必須項目です）")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("姓", key="last_name")
        st.text_input("ニックネーム *", key="nickname")
        st.selectbox("大学名 *", JAPANESE_UNIVERSITIES, index=None, placeholder="大学名を選択または入力して検索...", key="university")
        st.selectbox("出身地 *", PREFECTURES, index=None, placeholder="都道府県を選択または入力して検索...", key="hometown")
    with col2:
        st.text_input("名", key="first_name")
        st.date_input("誕生日", min_value=datetime.date(1980, 1, 1), max_value=datetime.date(2010, 12, 31), value=None, key="birth_date")
        st.selectbox("学部 *", DEPARTMENTS, index=None, placeholder="学部・学科を選択または入力して検索...", key="department")

    st.divider()

    st.subheader("趣味")
    for i in range(len(st.session_state.hobbies)):
        input_col, delete_col = st.columns([4, 1])
        with input_col:
            st.session_state.hobbies[i] = st.text_input(f"{i + 1}つ目", value=st.session_state.hobbies[i], key=f"hobby_{i}", label_visibility="collapsed")
        with delete_col:
            st.button("削除", key=f"delete_hobby_{i}", on_click=delete_hobby, args=(i,), use_container_width=True)
    st.button("＋追加", on_click=add_hobby, key="add_hobby")

    st.subheader("タグ")
    for i in range(len(st.session_state.tags)):
        input_col, delete_col = st.columns([4, 1])
        with input_col:
            st.session_state.tags[i] = st.text_input(f"{i + 1}つ目", value=st.session_state.tags[i], key=f"tag_{i}", label_visibility="collapsed", placeholder="例: カフェ好き")
        with delete_col:
            st.button("削除", key=f"delete_tag_{i}", on_click=delete_tag, args=(i,), use_container_width=True)
    st.button("＋追加", on_click=add_tag, key="add_tag")

    st.divider()

    st.text_area("話すと嬉しくなること", placeholder="例: おすすめの映画について話したいです！", key="happy_topic")
    st.text_area("ちょっと詳しいこと", placeholder="例: 美味しいコーヒーの淹れ方には自信があります", key="expert_topic")
    st.write("")

    if st.button("自己紹介を自動生成する！", use_container_width=True, type="primary"):
        if not st.session_state.nickname or not st.session_state.university or not st.session_state.hometown or not st.session_state.department:
            st.error("「*」が付いている項目はすべて選択・入力してください。")
        else:
            with st.spinner("AIがあなたの自己紹介を生成中です..."):
                hobbies = [h for h in st.session_state.hobbies if h]
                tags = [tag.strip().lstrip("#") for tag in st.session_state.tags if tag.strip()]
                
                profile_data = {
                    "id": st.session_state.user['id'], ### 変更：ログインユーザーのIDを追加
                    "last_name": st.session_state.last_name, "first_name": st.session_state.first_name,
                    "nickname": st.session_state.nickname, 
                    "birth_date": st.session_state.birth_date.strftime("%Y-%m-%d") if st.session_state.birth_date else None,
                    "university": st.session_state.university,
                    "department": st.session_state.department, "hometown": st.session_state.hometown,
                    "hobbies": hobbies,
                    "happy_topic": st.session_state.happy_topic, "expert_topic": st.session_state.expert_topic,
                    "tags": tags
                }
                response = manager.create_profile(profile_data)

            if response:
                st.success("自己紹介が完成しました！")
                st.balloons()
                with st.container(border=True):
                    st.subheader(f"🎉 {response.get('nickname')}さんのプロフィール")
                    generated_profile = response.get('generated_profile', {})
                    animal_result = response.get('animal_result', {})
                    st.write(f"**{generated_profile.get('catchphrase', '')}**")
                    st.write(generated_profile.get('introduction_comment', ''))
                    st.subheader(f"あなたのイメージ: **{animal_result.get('name', '')}**")
                    st.write(animal_result.get('reason', ''))
            else:
                st.error("自己紹介の生成に失敗しました。")