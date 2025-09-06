import streamlit as st
from datetime import datetime


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


def display_profile_detail(profile: dict):
    """
    指定されたプロフィール辞書の詳細を描画する関数コンポーネント。
    ネストされたデータ構造とフラットなデータ構造の両方に対応。
    """
    
    # --- データを取得するための準備 ---
    gen_profile = profile.get('generated_profile', {})
    basic_info = gen_profile.get('basic_info', {})
    talk_topics = gen_profile.get('talk_topics', {})
    animal_result = profile.get('animal_result', {})
    
    col1,col2=st.columns([1,2])

    with col1:
        st.image(
            profile.get('profile_image_url', 'https://placehold.co/150x150/EFEFEF/333333?text=No+Img'),
            width=150
        )

    with col2:
        st.subheader(profile.get('nickname', 'No Name'))
        
        # ### 修正 ### `basic_info` とトップレベルの両方から姓・名を取得
        last_name_val = basic_info.get("last_name") or profile.get("last_name", "")
        first_name_val = basic_info.get("first_name") or profile.get("first_name", "")
        full_name=f"{last_name_val} {first_name_val}"

        st.markdown(f"<p style='color: grey; margin-top: -10px;'>{full_name}</p>", unsafe_allow_html=True)
        st.caption(f"{gen_profile.get('catchphrase') or profile.get('catchphrase', '')}")
        tags=profile.get('tags',[])
        if tags:
            tag_spans="".join([f"<span style='background-color:#F0F2F6; border-radius:5px; padding:2px 6px; margin-right:4px;'>#{tag.lstrip('#')}</span>" for tag in tags])
            st.markdown(tag_spans, unsafe_allow_html=True)
            
    st.divider()

    # 動物診断結果
    with st.container(border=True):
        animal_icon_col, animal_text_col = st.columns([0.5, 3]) 

        with animal_icon_col:
            st.image(
                profile.get('animal_image_url', 'https://placehold.co/60x60/cccccc/333333?text=AI'),
                width=45 
            )

        with animal_text_col:
            category = animal_result.get('category') or profile.get('animal_category', 'カテゴリ未分類')
            st.markdown(f"**{category}**")
            
            animal_name = animal_result.get('name') or profile.get('animal_name')
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
            
    st.write("") 

    # 自己紹介
    introduction_text = gen_profile.get('introduction_comment') or profile.get('introduction_text', '自己紹介文がありません。')
    st.markdown("#### 自己紹介")
    st.write(introduction_text)

    # 詳細情報
    st.markdown("#### 詳細情報")
    colA,colB=st.columns(2)
    with colA:
        birth_date_str = basic_info.get('birth_date') or profile.get('birth_date')
        if birth_date_str:
            dt_obj = datetime.strptime(birth_date_str, '%Y-%m-%d')
            birth_date_formatted = f"{dt_obj.month}月{dt_obj.day}日"
        else:
            birth_date_formatted = '未設定'
        st.markdown(f"**誕生日:** {birth_date_formatted}")
        
        hometown = basic_info.get('hometown') or profile.get('hometown', '未設定')
        st.markdown(f"**出身地:** {hometown}")
        
        university = basic_info.get('university') or profile.get('university', '未設定')
        st.markdown(f"**大学:** {university}")
        
    with colB:
        hobbies_list = profile.get('hobbies', [])
        if hobbies_list:
            hobbies_text = ", ".join(hobbies_list)
        else:
            hobbies_text = talk_topics.get('hobbies', '未設定')
        st.markdown(f"**趣味:** {hobbies_text}")

        happy_topic = talk_topics.get('happy_topic') or profile.get('happy_topic', '未設定')
        st.markdown(f"**話したいこと:** {happy_topic}")

        expert_topic = talk_topics.get('expert_topic') or profile.get('expert_topic', '未設定')
        st.markdown(f"**詳しいこと:** {expert_topic}")

def render_profile_card(profile: dict,target_col):
    """
    プロフィールカードを描画する関数
    """
    st.markdown(f"### {profile.get('nickname', 'No Name')}")

