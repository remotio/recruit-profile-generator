import streamlit as st
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY  # 設定情報をインポート
import supabase_utils  # DB操作関数をインポート
import profile_manager
from components import render_nav_banner
import sys
import os

# --- アプリケーションの初期化処理 ---
# Supabaseへの接続を確立する
supabase:Client=create_client(SUPABASE_URL,SUPABASE_KEY)
# Profile_managerの初期化
profile_manager=profile_manager.ProfileManager(supabase)


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views import all_profiles_view, my_page_view, create_profile_view

st.set_page_config(
    page_title="内定者図鑑ジェネレーター",
    layout="wide"
)


render_nav_banner()


if 'active_page' not in st.session_state:
    st.session_state.active_page = "みんなの図鑑"

if st.session_state.active_page == "みんなの図鑑":
    all_profiles_view.render_page()
elif st.session_state.active_page == "マイページ":
    my_page_view.render_page()
elif st.session_state.active_page == "プロフィール作成":
    create_profile_view.render_page()
