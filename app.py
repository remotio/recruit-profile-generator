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

