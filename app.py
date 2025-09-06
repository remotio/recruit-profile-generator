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
if 'supabase_client' not in st.session_state:
    st.session_state.supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Profile_managerの初期化
    st.session_state.profile_manager = profile_manager.ProfileManager(st.session_state.supabase_client)

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
                user=st.session_state.profile_manager.sign_up(email,password)
                st.session_state.user=user
                st.success("新規登録に成功しました!")
                st.rerun()
            except Exception as e:
                st.error(f"新規登録に失敗しました: {e}")
        if st.button("ログイン"):
            try:
                user=st.session_state.profile_manager.sign_in(email,password)
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

# ログイン状態に応じたメイン画面の表示
# ログイン&プロフ作成済み/ログインのみ/未ログインの3パターンで表示を分ける
if st.session_state.user:
    st.info(f"ようこそ、{st.session_state.user['email']}さん!")
    current_user_id=st.session_state.user['id']
    profile_exists=st.session_state.profile_manager.check_profile_exists(current_user_id)
    if not profile_exists:
        st.info("ようこそ!まずはあなたのプロフィールを作成しましょう。")
        #ここにフォームを置く
    else:
        #ここにメイン画面を表示する
        st.title("プロフィール")#インデントエラー回避の仮
else:
    # 変更点：ログインしていなくても閲覧は許可するため、警告をソフトな案内に変更
    st.info("サイドバーからログインすると、マイページの編集やAIによる会話のヒント機能が利用できます。")


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views import all_profiles_view, my_page_view, create_profile_view

st.set_page_config(
    page_title="内定者図鑑ジェネレーター",
    layout="wide"
)


render_nav_banner()

# 変更点：ログイン必須の st.stop() を削除し、ページごとの認証チェックに移行

if 'active_page' not in st.session_state:
    st.session_state.active_page = "みんなの図鑑"


# ページごとのルーティングと認証チェック
if st.session_state.active_page == "みんなの図鑑":
    # 「みんなの図鑑」はログインしていなくても表示を許可する
    # all_profiles_view.py 側が user の有無をチェックするため、そのまま呼び出す
    all_profiles_view.render_page()

elif st.session_state.active_page == "マイページ":
    # 「マイページ」はログインが必要
    if st.session_state.user:
        my_page_view.render_page()
    else:
        st.warning("マイページを表示するには、サイドバーからログインしてください。")

elif st.session_state.active_page == "プロフィール作成":
    # 「プロフィール作成」もログインが必要
    if st.session_state.user:
        create_profile_view.render_page()
    else:
        st.warning("プロフィールを作成・編集するには、サイドバーからログインしてください。")