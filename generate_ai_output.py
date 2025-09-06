import os
from dotenv import load_dotenv
from supabase import create_client, Client
from rich.progress import track  # 進行状況をきれいに表示するためのライブラリ


# --- モジュールのインポート ---
from profile_manager import ProfileManager, UserInput

def main():
    """
    全ユーザーのAI関連情報を一括で再生成し、データベースを更新するスクリプト。
    """
    print("🚀 AI情報の一括更新スクリプトを開始します。")

    # 1. 環境変数を読み込む
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ エラー: .envファイルにSupabaseのURLとキーを設定してください。")
        return

    # 2. クライアントとマネージャーを初期化
    supabase_client: Client = create_client(supabase_url, supabase_key)
    profile_manager = ProfileManager(supabase_client)

    try:
        # 3. 全ユーザーのプロフィールを取得
        # get_all_profilesは自分を除外する仕様なので、一時的に全ユーザーを取得する関数を直接呼び出す
        print("🔄 全ユーザーのプロフィールを取得中...")
        all_profiles_response = supabase_client.table('profiles').select("*").execute()
        all_profiles = all_profiles_response.data
        print(f"✅ {len(all_profiles)}人のユーザーが見つかりました。")

        # 4. 各ユーザーの情報をループして更新
        # rich.progress.trackでループを囲むと、プログレスバーが表示される
        for profile in track(all_profiles, description="AI情報を生成・更新中..."):
            user_id = profile['id']
            
            # UserInput型に準拠したデータを作成
            user_input: UserInput = {
                key: profile[key] for key in UserInput.__annotations__.keys() if key in profile
            }
            
            # ProfileManagerの更新メソッドを呼び出す
            profile_manager.update_user_input(user_id, user_input)

        print("\n🎉 全てのユーザー情報の更新が完了しました！")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()