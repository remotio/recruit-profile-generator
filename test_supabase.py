# test_supabase.py
import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_supabase_connection():
    load_dotenv()

    # SupabaseのURLとキーを取得
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        print("エラー: SUPABASE_URLまたはSUPABASE_KEYが設定されていません。.envファイルを確認してください。")
        return

    print("Supabaseに接続中...")

    try:
        # Supabaseクライアントを初期化
        supabase: Client = create_client(url, key)

        # 'profiles'テーブルから全てのデータを取得
        response = supabase.table('profiles').select("*").execute()

        # 取得したデータを表示
        print("\n--- 取得したデータ ---")
        for user in response.data:
            print(f"  - ユーザー名: {user['username']}, 自己紹介: {user['introduction_text']}")
        print("----------------------\n")
        print("✅ Supabaseの接続テストに成功しました！")

    except Exception as e:
        print(f"❌ Supabase接続中にエラーが発生しました: {e}")

if __name__ == "__main__":
    test_supabase_connection()