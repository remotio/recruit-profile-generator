import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY  # 設定情報をインポート
import supabase_utils  # DB操作関数をインポート
import profile_manager

# --- アプリケーションの初期化処理 ---
# Supabaseへの接続を確立する
supabase:Client=create_client(SUPABASE_URL,SUPABASE_KEY)
# Profile_managerの初期化
profile_manager=profile_manager.ProfileManager(supabase)
# 認証状態の初期化
if 'user' not in st.session_state:
    st.session_state.user=None

# 一旦サイドバーを用いたログインフォームを実装
with st.sidebar:
    st.header("認証")
    if st.session_state.user is None:
        email=st.text_input("メールアドレス")
        password=st.text_input("パスワード",type="password")

        if st.button("新規登録"):
            try:
                user=profile_manager.sign_up(email,password)
                st.session_state.user=user
                st.success("新規登録に成功しました!")
                st.rerun()
            except Exception as e:
                st.error(f"新規登録に失敗しました: {e}")
        if st.button("ログイン"):
            try:
                user=profile_manager.sign_in(email,password)
                st.session_state.user=user
                st.success("ログインに成功しました!")
                st.rerun()
            except Exception as e:
                st.error(f"{e}")
    else:
        st.write(f"ログイン中: {st.session_state.user['email']}")
        if st.button("ログアウト"):
            st.session_state.user=None
            st.success("ログアウトしました")
            st.rerun()
if st.session_state.user:
    st.info(f"ようこそ、{st.session_state.user['email']}さん!")
