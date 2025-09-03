import streamlit as st
from datetime import datetime

# コンポーネントの取得
supabase_client=st.session_state.supabase_client
profile_manager=st.session_state.profile_manager
current_user=st.session_state.user

st.markdown("""
<style>
.left-col-image {
    width: 150px;
    height: 150px;
    border-radius: 50%; /* 画像を円形にする */
    object-fit: cover; /* 画像のアスペクト比を保ちつつコンテナにフィットさせる */
}
.right-col-content h2 {
    margin-top: 0; /* 名前の上の余白をなくす */
    margin-bottom: 0.5rem; /* 名前と動物名の間のスペース */
}
.right-col-content h4 {
    color: grey; /* 動物名を少し薄い色に */
    margin-top: 0; /* 動物名の上の余白をなくす */
    margin-bottom: 0.5rem; /* 動物名と動物画像との間のスペース */
}
.right-col-content img {
    width: 80px; /* 動物画像のサイズ */
    height: 80px;
    border-radius: 10px; /* 動物画像の角を少し丸める */
}
</style>
""", unsafe_allow_html=True)


def display_profile_detail(profile_id: str):
    """
    指定されたIDのプロフィール詳細をモーダル内に描画する関数コンポーネント
    """

    try:
        profile = profile_manager.get_profile_by_id(profile_id)
    except Exception as e:
        st.error(f"プロフィールの取得中にエラーが発生しました: {e}")
        return
    
    col1,col2=st.columns([1,2])

    with col1:
        st.image(
            profile.get('profile_image_url', 'https://placehold.co/150x150/EFEFEF/333333?text=No+Img'),
            width=150
        )

    with col2:
        st.subheader(profile.get('nickname', 'No Name'))
        full_name=f"{profile.get('last_name','')} {profile.get('first_name','')}"
        st.markdown(f"<p style='color: grey; margin-top: -10px;'>{full_name}</p>", unsafe_allow_html=True)
        st.caption(f"{profile.get('catchphrase', '')}")
        tags=profile.get('tags',[])
        if tags:
            tag_spans="".join([f"<span style='background-color:#F0F2F6; border-radius:5px; padding:2px 6px; margin-right:4px;'>#{tag.lstrip('#')}</span>" for tag in tags])
            st.markdown(tag_spans, unsafe_allow_html=True)
            
    st.divider()

    # 動物診断結果
    with st.container(border=True):
        animal_icon_col, animal_text_col = st.columns([0.5, 3]) # アイコンとテキストの比率

        with animal_icon_col:
            # 動物の画像をアイコンとして表示
            st.image(
                profile.get('animal_image_url', 'https://placehold.co/60x60/cccccc/333333?text=AI'),
                width=45 # 小さなアイコンサイズ
            )

        with animal_text_col:
            st.markdown(f"**{profile.get('animal_category', 'カテゴリ未分類')}**")
            
            animal_name = profile.get('animal_name')
            if animal_name:
                html_content = f"""
                <div style="display: flex; align-items: baseline; margin-top: -10px;">
                  <span style="font-size: 1.5em; font-weight: 600; margin-right: 5px; line-height: 1.2;">{animal_name}</span>
                  <span style="font-size: 0.8em; color: grey;">タイプ</span>
                </div>
                """
            else:
                html_content = f"""
                <div style="margin-top: -10px;">
                  <span style="font-size: 1.75em; font-weight: 600; color: grey;">診断中...</span>
                </div>
                """
            st.markdown(html_content, unsafe_allow_html=True)
            
    st.write("") # スペース

    # 自己紹介
    st.markdown("#### 自己紹介")
    st.write(profile.get('introduction_text','自己紹介文がありません。'))

    # 詳細情報
    st.markdown("#### 詳細情報")
    colA,colB=st.columns(2)
    with colA:
        birth_date_str = profile.get('birth_date')
        if birth_date_str:
            # 1. まず、どの環境でも動作するstrptimeで日付オブジェクトに変換
            dt_obj = datetime.strptime(birth_date_str, '%Y-%m-%d')
            
            # 2. f-stringで直接、月と日の数値を文字列に埋め込む
            birth_date_formatted = f"{dt_obj.month}月{dt_obj.day}日"
        else:
            birth_date_formatted = '未設定'
        st.markdown(f"**誕生日:**  {birth_date_formatted}")
        st.markdown(f"**出身地:**  {profile.get('hometown', '未設定')}")
        st.markdown(f"**大学:**  {profile.get('university', '未設定')}")
    with colB:
        st.markdown(f"**趣味:** {', '.join(profile.get('hobbies', []))}")
        st.markdown(f"**話したいこと:** {profile.get('happy_topic', '未設定')}")
        st.markdown(f"**詳しいこと:** {profile.get('expert_topic', '未設定')}")