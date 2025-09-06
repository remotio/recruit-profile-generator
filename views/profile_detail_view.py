# views/profile_detail_view.py
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
import profile_manager

def render_page():
    profile_manager = st.session_state.profile_manager

    # app.pyがURLから読み取って保存したIDを取得
    try:
        profile_id = st.session_state.target_profile_id
    except AttributeError:
        st.error("表示するユーザーが指定されていません。")
        st.stop()
        
    try:
        profile = profile_manager.get_profile_by_id(profile_id)
        
        # --- ここに、all_profiles_view.pyのexpander内にあった
        # --- 詳細表示のロジックを全てコピー＆ペーストする ---
        st.title(f"{profile.get('nickname')}さんのプロフィール")
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
            st.markdown(f"**誕生日:**  {birth_date_formatted}")
            st.markdown(f"**出身地:**  {profile.get('hometown', '未設定')}")
            st.markdown(f"**大学:**  {profile.get('university', '未設定')}")
        with colB:
            st.markdown(f"**趣味:** {', '.join(profile.get('hobbies', []))}")
            st.markdown(f"**話したいこと:** {profile.get('happy_topic', '未設定')}")
            st.markdown(f"**詳しいこと:** {profile.get('expert_topic', '未設定')}")
    except ValueError as e:
        st.error(f"プロフィールの読み込みに失敗しました: {e}")