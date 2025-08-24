import streamlit as st

st.set_page_config(layout="wide")
st.title("🚀 環境構築チェック 🚀")
st.success("Streamlitアプリが正常に起動しました！")

st.divider()

st.subheader("✅ APIキーの確認")
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]

    if gemini_key and supabase_url and supabase_key:
        st.success("secrets.toml から全てのAPIキーを読み込めました！")
        st.balloons()
    else:
        st.warning("キーが空のようです。secrets.toml ファイルを確認してください。")
except Exception as e:
    st.error(f"secrets.tomlの読み込みに失敗しました。ファイルが存在するか確認してください。エラー: {e}")