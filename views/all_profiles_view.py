import streamlit as st
from profile_manager import ProfileManager
from streamlit_modal import Modal
import sys
import os
from datetime import datetime
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

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

     # 1. 検索フォームを配置
    search_query = st.text_input("名前やキーワードで検索", key="search_input")
    
    if st.button("検索", key="search_button"):
        # 2. 検索ボタンが押されたら、バックエンドの検索機能を呼び出す
        current_user_id = st.session_state.user['id']
        with st.spinner("検索中..."):
            st.session_state.search_results = profile_manager.search_profiles(
                current_user_id=current_user_id,
                query=search_query
            )
    
    # 3. セッションステートに検索結果があるかどうかで、表示を切り替える
    if 'search_results' in st.session_state and st.session_state.search_results is not None:
        # --- 検索結果がある場合の表示 ---
        st.markdown("##### 🔎 検索結果")
        search_results = st.session_state.search_results
        
        if not search_results:
            st.info("検索結果に合致するユーザーは見つかりませんでした。")
        else:
            # 検索結果をカード形式で表示
            cols = st.columns(2)
            for i, profile in enumerate(search_results):
                target_col = cols[i % 2]
                render_profile_card(profile, target_col)
        
        # 検索結果をリセットするためのボタン
        if st.button("一覧に戻る", key="reset_search_button"):
            st.session_state.search_results = None
            st.rerun() # ページを再読み込みして一覧表示に戻す
    else:
        # この行を追加して、suggested_profilesを必ず初期化する
        suggested_profiles = []

        if st.session_state.user:
            with st.spinner("あなたにぴったりの人を探しています..."):
                try:
                    # 1. 自分に似ているユーザーを10人取得する
                    similar_profiles = profile_manager.find_similar_profiles(st.session_state.user['id'])
                    
                    # 表示する類似ユーザーを格納するリスト
                    if similar_profiles:
                        # 2. 10人の中からランダムに表示する人を決める（最大二人）
                        sample_count = min(len(similar_profiles), 2)
                        suggested_profiles = random.sample(similar_profiles, k=sample_count)

                    # 3. 類似ユーザーを表示するセクション
                    if suggested_profiles:
                        st.markdown("##### 💡 あなたと属性が近いかも...？")
                        cols = st.columns(len(suggested_profiles)) # 1人なら1列、2人なら2列
                        for i, profile in enumerate(suggested_profiles):
                            # 既存のカード描画関数を再利用
                            render_profile_card(profile, cols[i])
                        st.divider()

                except Exception as e:
                    # 類似ユーザー検索に失敗しても、ページ全体が停止しないようにする
                    st.toast(f"類似ユーザーの取得に失敗しました: {e}", icon="⚠️")
                    # エラー時も初期化されているので、この行は削除
                    # suggested_profiles = [] 

        with st.spinner("みんなのプロフィールを読み込んでいます..."):
            try:
                # ログインしているかチェック
                if st.session_state.user:
                    # ログインしていれば、自分のIDを渡して自分を除外
                    current_user_id = st.session_state.user['id']
                    profiles = profile_manager.get_all_profiles(current_user_id)
                else:
                    # ログインしていなければ、引数なしで呼び出し、全ユーザーを取得
                    profiles = profile_manager.get_all_profiles()
            except Exception as e:
                st.error(f"プロフィールの取得中にエラーが発生しました: {e}")
                return 

        if not profiles:
            st.info("まだ誰も登録していません。")
        else:
            # 1. 提案セクションに表示されたユーザーのIDのセットを作成
            suggested_ids = {p['id'] for p in suggested_profiles}
            # 2. メインの一覧から、提案済みのユーザーを除外する
            main_list_profiles = [p for p in profiles if p['id'] not in suggested_ids]
            cols = st.columns(2)
            for i, profile in enumerate(main_list_profiles):
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
            # 1. 表示するURLを事前に決定する
            profile_img_url = profile.get('profile_image_url')
            if not profile_img_url:
                profile_img_url = 'https://placehold.co/100x100/EFEFEF/333333?text=No+Img'
            # 動物の名前を取得
            animal_name_card = profile.get('animal_name')
            # 動物名から画像データ(Base64)を取得
            if animal_name_card:
                animal_image_data_card = profile_manager.assign_animal_image_url(animal_name_card)
            else:
                animal_image_data_card = 'https://placehold.co/40x40/cccccc/333333?text=AI'

            st.markdown(f"""
            <div class="card-top-content">
                 <div class="image-container">
                    <img class="profile-image" src="{profile_img_url}">
                    <img class="animal-image" src="{animal_image_data_card}">
                </div>
                <h4 style='text-align: center; ...'>{profile['nickname']}</h4>
                <p style='text-align: center; ...'>{profile.get('last_name', '')} {profile.get('first_name', '')}</p>
            </div>
            """, unsafe_allow_html=True)


            # --- 詳細表示用のExpander ---
            with st.expander("もっと見る"):
                # 詳細ヘッダー
                col1, col2 = st.columns([1, 2])
                with col1:
                    image_url=profile.get('profile_image_url')
                    if image_url and image_url.startswith('http'):
                        st.image(image_url, width=150)
                    else:
                        st.image('https://placehold.co/150x150/EFEFEF/333333?text=No+Img', width=150)
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
                    animal_icon_col, animal_text_col = st.columns([1, 2]) # アイコンとテキストの比率

                    with animal_icon_col:
                        # 1. 動物の名前を取得
                        animal_name_detail = profile.get('animal_name')
                        # 2. 動物名から画像データ(Base64)を取得
                        if animal_name_detail:
                            animal_image_data_detail = profile_manager.assign_animal_image_url(animal_name_detail)
                        else:
                            animal_image_data_detail = 'https://placehold.co/60x60/cccccc/333333?text=Animal'
                        
                        # 3. 取得した画像データを表示
                        st.image(animal_image_data_detail, width=45)

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
                    st.markdown(f"**誕生日:** {birth_date_formatted}")
                    st.markdown(f"**出身地:** {profile.get('hometown', '未設定')}")
                    st.markdown(f"**大学:** {profile.get('university', '未設定')}")
                with colB:
                    st.markdown(f"**趣味:** {', '.join(profile.get('hobbies', []))}")
                    st.markdown(f"**話したいこと:** {profile.get('happy_topic', '未設定')}")
                    st.markdown(f"**詳しいこと:** {profile.get('expert_topic', '未設定')}")
                
                if st.session_state.user:
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
                    st.divider()
                    st.markdown("#### このユーザーに関するメモ")

                    current_user_id = st.session_state.user['id']
                    target_user_id = profile['id']

                    # 1. 既存のメモを取得して表示
                    try:
                        existing_memo = profile_manager.get_memo_for_target(current_user_id, target_user_id)
                        memo_content = existing_memo['content'] if existing_memo else ""
                    except Exception as e:
                        st.error(f"メモの読み込みに失敗しました: {e}")
                        memo_content = "" # エラー時は空にする

                    # 2. メモ入力用のテキストエリアを配置
                    new_memo = st.text_area(
                        "メモを編集:", 
                        value=memo_content, 
                        key=f"memo_{profile['id']}",
                        height=150
                    )

                    # 3. 保存ボタンと削除ボタンを横並びに配置
                    col_save, col_delete = st.columns(2)
                    with col_save:
                        if st.button("メモを保存", key=f"save_memo_{profile['id']}", use_container_width=True):
                            try:
                                profile_manager.save_memo(current_user_id, target_user_id, new_memo)
                                st.success("メモを保存しました。")
                                # ページをリロードして、表示を最新の状態に更新
                                st.rerun() 
                            except Exception as e:
                                st.error(f"メモの保存に失敗しました: {e}")
                    
                    with col_delete:
                        if st.button("メモを削除", key=f"delete_memo_{profile['id']}", use_container_width=True):
                            try:
                                profile_manager.delete_memo(current_user_id, target_user_id)
                                st.success("メモを削除しました。")
                                st.rerun()
                            except Exception as e:
                                st.error(f"メモの削除に失敗しました: {e}")