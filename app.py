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
    
# プロフィール存在状態のキャッシュを初期化
if 'profile_exists' not in st.session_state:
    st.session_state.profile_exists = False

query_params = st.query_params
if "page" in query_params and query_params["page"]=="profile_detail":
    st.session_state.active_page="プロフィール詳細"
    if "id" in query_params:
        st.session_state.target_profile_id=query_params["id"]


def logout():
    """
    st.session_stateの全てのキーを削除して，セッションをリセットする．
    """
    # st.session_stateのキーをリストに変換して、安全にループ処理
    keys_to_delete = list(st.session_state.keys())
    for key in keys_to_delete:
        del st.session_state[key]
    
    st.success("ログアウトしました")

# 一旦サイドバーを用いたログインフォームを実装
with st.sidebar:
    st.header("認証")
    if st.session_state.user is None:
        email=st.text_input("メールアドレス")
        password=st.text_input("パスワード",type="password")

        if st.button("新規登録"):
            if not email or not password:
                st.error("メールアドレスとパスワードは必須です。")
            else:
                try:
                    user=st.session_state.profile_manager.sign_up(email,password)
                    st.session_state.user=user
                    # 新規登録直後はプロフィールがないため、Falseに設定
                    st.session_state.profile_exists = False 
                    st.success("新規登録に成功しました!")
                    st.rerun()
                except Exception as e:
                    st.error(f"新規登録に失敗しました: {e}")
        if st.button("ログイン"):
            if not email or not password:
                st.error("メールアドレスとパスワードは必須です。")
            else:
                try:
                    user=st.session_state.profile_manager.sign_in(email,password)
                    st.session_state.user=user
                    # ログイン時はプロフィールの存在を再チェック
                    current_user_id=st.session_state.user['id']
                    st.session_state.profile_exists=st.session_state.profile_manager.check_profile_exists(current_user_id)
                    st.success("ログインに成功しました!")
                    st.rerun()
                except Exception as e:
                    st.error(f"{e}")
    else:
        st.write(f"ログイン中: {st.session_state.user['email']}")
        if st.button("ログアウト", on_click=logout):
            pass

# ログイン状態に応じたメイン画面の表示
if st.session_state.user:
    st.toast(f"ようこそ、{st.session_state.user['email']}さん!")
    current_user_id=st.session_state.user['id']
    profile_exists=st.session_state.profile_manager.check_profile_exists(current_user_id)
    # プロフィール存在状態をセッションにキャッシュ
    st.session_state.profile_exists = profile_exists
    if not profile_exists:
        st.info("ようこそ!まずはあなたのプロフィールを作成しましょう。")
else:
    st.info("サイドバーからログインすると、マイページの編集やAIによる会話のヒント機能が利用できます。")



sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views import all_profiles_view, my_page_view, create_profile_view,profile_detail_view

st.set_page_config(
    page_title="内定者図鑑ジェネレーター",
    layout="wide"
)

# ナビゲーションバーの表示ロジックを修正
# ログイン状態とプロフィール作成状態に応じて表示するボタンを切り替える
pages = ["みんなの図鑑"]
if st.session_state.user:
    if st.session_state.profile_exists:
        pages.append("マイページ")
    else:
        pages.append("プロフィール作成")

# pagesリストをrender_nav_bannerに渡す
render_nav_banner(pages=pages)

if 'active_page' not in st.session_state:
    st.session_state.active_page = "みんなの図鑑"
if st.session_state.active_page == "みんなの図鑑":
    all_profiles_view.render_page()

elif st.session_state.active_page == "マイページ":
    if st.session_state.user and st.session_state.profile_exists:
        my_page_view.render_page()
    else:
        st.warning("マイページを表示するには、プロフィールを作成する必要があります。")
        st.info("ナビゲーションバーから「プロフィール作成」ページに移動してください。")

elif st.session_state.active_page == "プロフィール作成":
    if st.session_state.user:
        create_profile_view.render_page()
    else:
        st.warning("プロフィールを作成・編集するには、サイドバーからログインしてください。")
elif st.session_state.active_page == "プロフィール詳細":
    profile_detail_view.render_page()
    
