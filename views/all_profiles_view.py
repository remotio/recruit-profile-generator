import streamlit as st
from profile_manager import ProfileManager
from streamlit_modal import Modal
import sys
import os
from datetime import datetime
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

    st.subheader("みんなのプロフィール", divider="blue")

    modal = Modal("", key="profile-modal", padding=20, max_width=700)

    with st.spinner("みんなのプロフィールを読み込んでいます..."):
        try:
            profiles = profile_manager.get_all_profiles(st.session_state.user['id'])
        except Exception as e:
            st.error(f"プロフィールの取得中にエラーが発生しました: {e}")
            return 

    if not profiles:
        st.info("まだ誰も登録していません。")
    else:
        cols = st.columns(2)
        for i, profile in enumerate(profiles):
            target_col = cols[i % 2]
            # 関数を呼び出してカードを描画
            render_profile_card(profile, target_col)

def render_profile_card(profile:dict,target_col):
    '''
        １人分のプロフカードと，その詳細を展開表示するExtenderを描画する関数
    '''
    with target_col:
        with st.container(border=True):
            # --- プロフィールカードのヘッダー部分 ---
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

            # --- 詳細表示用のExpander ---
            with st.expander("もっと見る"):
                # 詳細ヘッダー
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(profile.get('profile_image_url', 'https://placehold.co/150x150/EFEFEF/333333?text=No+Img'), width=150)
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
                
                # 会話のきっかけ
                # 1. セッションステートを初期化
                if f'conv_starter_{profile.get("id")}' not in st.session_state:
                    st.session_state[f'conv_starter_{profile.get("id")}'] = None

                # 2. ボタンが押されたら、APIを呼び出して結果をセッションステートに保存
                if st.button("AIに会話のヒントをもらう", key=f"conv_starter_button_{profile.get('id')}"):
                    current_user_id = st.session_state.user.get('id')
                    
                    if not current_user_id:
                        st.warning("ログイン情報が見つかりません。")
                    else:
                        try:
                            with st.spinner("AIが会話のヒントを考えています..."):
                                starters = profile_manager.generate_conversation_starters(
                                    my_id=current_user_id,
                                    opponent_id=profile.get("id")
                                )
                            # 結果をセッションステートに保存
                            st.session_state[f'conv_starter_{profile.get("id")}'] = starters
                        except Exception as e:
                            # エラーもセッションステートに保存
                            st.session_state[f'conv_starter_{profile.get("id")}'] = {"error": str(e)}

                # 3. セッションステートにデータがあれば、常に表示する
                starters_data = st.session_state[f'conv_starter_{profile.get("id")}']
                print(starters_data)
                if starters_data:
                    if "error" in starters_data:
                        st.error(f"ヒントの生成に失敗しました: {starters_data['error']}")
                    else:
                        with st.container(border=True):
                            st.markdown("**🤝 2人の共通点**")
                            if starters_data.get("common_points"):
                                for point in starters_data["common_points"]:
                                    st.markdown(f"- {point}")
                            
                            st.markdown("**💡 話題の提案**")
                            if starters_data.get("topics"):
                                for topic in starters_data["topics"]:
                                    st.info(topic)