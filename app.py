import streamlit as st
from dotenv import load_dotenv
from supabase import create_client, Client
import os
import google.generativeai as genai

# --- 初期設定 ---
load_dotenv()

# SupabaseとGeminiのクライアントを初期化
@st.cache_resource
def init_clients():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase = create_client(url, key)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return supabase

supabase = init_clients()
embedding_model = "gemini-embedding-001"

st.title("類似ユーザー検索 PoC")
st.write("Supabaseに保存されているユーザーを選択して、似ているユーザーを検索するテストです。")

# --- 1. ユーザー選択 ---
try:
    # Supabaseから全ユーザーのリストを取得
    profiles_res = supabase.table('profiles').select("id, username").order('id').execute()
    profiles = profiles_res.data
    
    # ユーザー名でドロップダウンリストを作成
    profile_usernames = [p['username'] for p in profiles]
    selected_username = st.selectbox("検索の基準となるユーザーを選んでください:", profile_usernames)

    # --- 2. 検索実行 ---
    if st.button("似ている人を探す"):
        if selected_username:
            st.divider()
            st.subheader(f"「{selected_username}」さんに似ているユーザー:")

            # 選択されたユーザーのIDと自己紹介文を取得
            selected_user_res = supabase.table('profiles').select("id, introduction_text").eq('username', selected_username).single().execute()
            selected_user = selected_user_res.data

            if not selected_user:
                st.error("選択されたユーザーが見つかりませんでした。")
            else:
                with st.spinner("ベクトルを生成し、検索を実行中..."):
                    # 「検索クエリ」としてベクトル化
                    response = genai.embed_content(
                        model=embedding_model,
                        content=selected_user['introduction_text'],
                        task_type="RETRIEVAL_QUERY"
                    )
                    query_embedding = response['embedding']

                    # Supabaseの関数を呼び出して検索を実行
                    result = supabase.rpc('match_profiles', {
                        'query_embedding': query_embedding,
                        'match_threshold': 0.7,
                        'match_count': 5
                    }).execute()
                
                # --- 3. 結果表示 ---
                if result.data:
                    found_match = False
                    for match in result.data:
                        if match['id'] != selected_user['id']:
                            st.success(f"**{match['username']}** (類似度: {match['similarity']:.4f})")
                            found_match = True
                    
                    if not found_match:
                        st.info("条件に合う類似ユーザーは見つかりませんでした。")
                else:
                    st.info("条件に合う類似ユーザーは見つかりませんでした。")
        else:
            st.warning("ユーザーを選択してください。")

except Exception as e:
    st.error(f"エラーが発生しました: {e}")
    st.info("Supabaseにデータが正しく登録されているか、APIキーが正しいか確認してください。")