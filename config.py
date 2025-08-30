import streamlit as st

# Supabaseの接続情報を取得
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Gemini APIのキーを取得
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]