import streamlit as st
from profile_manager import ProfileManager
from streamlit_modal import Modal
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from views.profile_detail_component import display_profile_detail


supabase_client=st.session_state.supabase_client
profile_manager=st.session_state.profile_manager
current_user=st.session_state.user

def render_page():
    st.markdown("""
    <style>
    /* Streamlitが生成するコンテナ自体にスタイルを適用する */
    div[data-testid="stVerticalBlock"]:has(button[data-testid="baseButton-secondary"]) > div[data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-top-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
    }
    .image-container {
        position: relative;
        width: 100px;
        height: 100px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .profile-image {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        object-fit: cover;
        border: 4px solid #F0F2F6;
    }
    .animal-image {
        position: absolute;
        bottom: -5px;
        right: -5px;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        background: white;
        padding: 2px;
    }
    div[data-testid="stModal"] h1 {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

    st.subheader("みんなのプロフィール", divider="blue")

    modal = Modal("", key="profile-modal", padding=20, max_width=700)

    def open_modal_with_id(p_id):
        st.session_state['selected_profile_id'] = p_id
        modal.open()

    with st.spinner("みんなのプロフィールを読み込んでいます..."):
        profiles = profile_manager.get_all_profiles(st.session_state.user['id'])

    if not profiles:
        st.info("まだ誰も登録していません。")
    else:
        cols = st.columns(2)
        for i, profile in enumerate(profiles):
            target_col = cols[i % 2]
            
            with target_col:
                with st.container(border=True, height=380):
                    st.markdown(f"""
                    <div class="card-top-content">
                        <div class="image-container">
                            <img class="profile-image" src="{profile.get('profile_image_url', 'https://placehold.co/100x100/EFEFEF/333333?text=No+Img')}">
                            <img class="animal-image" src="{profile.get('animal_image_url', 'https://placehold.co/40x40/cccccc/333333?text=AI')}">
                        </div>
                        <h4 style='text-align: center; margin-bottom: 0.25rem;'>{profile['nickname']}</h4>
                        <p style='text-align: center; color: grey; font-size: 0.9em;'>{profile.get('university', '')} / {profile.get('department', '')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.button(
                        "もっと見る", 
                        key=profile['id'],
                        on_click=open_modal_with_id, 
                        args=(profile['id'],),
                        use_container_width=True
                    )

    if modal.is_open():
        with modal.container():
            if 'selected_profile_id' in st.session_state and st.session_state['selected_profile_id'] is not None:
                profile_id = st.session_state['selected_profile_id']
                display_profile_detail(profile_id)
            else:
                st.warning("表示するプロフィールが選択されていません。")
