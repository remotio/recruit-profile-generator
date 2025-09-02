import streamlit as st
from profile_manager import ProfileManager

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
    profile = profile_manager.get_profile_by_id(profile_id)

    if not profile:
        st.error("プロファイルが見つかりませんでした。")
        return

    left_col, right_col = st.columns([2, 3])

    with left_col:
        st.markdown(f"""
        <img class="left-col-image" src="{profile.get('profile_image_url', 'https://placehold.co/150x150/EFEFEF/333333?text=No+Img')}">
        """, unsafe_allow_html=True)

    with right_col:
        animal_result = profile.get('animal_result', {})
        st.markdown(f"""
        <div class="right-col-content">
            <h2>{profile.get('nickname', 'No Name')}</h2>
            <h4>{animal_result.get('name', '')}</h4>
            <img src="{profile.get('animal_image_url', 'https://placehold.co/80x80/cccccc/333333?text=AI')}">
        </div>
        """, unsafe_allow_html=True)


    st.write("")
    st.divider()

    intro_comment = profile.get('generated_profile', {}).get('introduction_comment', '自己紹介文がありません。')
    st.markdown(intro_comment)
    st.write("")

    basic_info = profile.get('generated_profile', {}).get('basic_info', {})
    talk_topics = profile.get('generated_profile', {}).get('talk_topics', {})
    
    details_col1, details_col2 = st.columns(2)
    with details_col1:
        st.markdown(f"**大学**")
        st.write(f"{basic_info.get('university', '未設定')} / {basic_info.get('department', '未設定')}")
        st.markdown(f"**話すと嬉しくなること**")
        st.write(talk_topics.get('happy_topic', '未設定'))
    with details_col2:
        st.markdown(f"**出身地**")
        st.write(basic_info.get('hometown', '未設定'))
        st.markdown(f"**ちょっと詳しいこと**")
        st.write(talk_topics.get('expert_topic', '未設定'))
    
    st.write("") 


    tags = profile.get('generated_profile', {}).get('tags', [])
    if tags:
        tag_html = " ".join([f"`#{tag.lstrip('#')}`" for tag in tags])
        st.markdown(f"**タグ:** {tag_html}")