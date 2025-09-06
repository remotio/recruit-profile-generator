# backfill_search_text.py

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from rich.progress import track
from typing import List

def create_searchable_text(profile: dict) -> str:
    """
    プロフィール辞書から、検索用の結合テキストを生成する。
    （トリガー関数内のロジックと全く同じものです）
    """
    parts = [
        profile.get('last_name', ''),
        profile.get('first_name', ''),
        profile.get('nickname', ''),
        profile.get('catchphrase', ''),
        profile.get('introduction_text', ''),
        profile.get('university', ''),
        profile.get('hometown', ''),
        profile.get('happy_topic', ''),
        profile.get('expert_topic', ''),
        ' '.join(profile.get('hobbies', [])),
        ' '.join(profile.get('tags', []))
    ]
    # Noneや空文字を除外して結合
    return ' '.join(filter(None, parts))

def main():
    """
    既存の全プロフィールのsearchable_textカラムを更新（バックフィル）するスクリプト。
    """
    print("🚀 searchable_textカラムのバックフィル処理を開始します。")
    # 1. 環境変数を読み込む
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ エラー: .envファイルにSupabaseのURLとキーを設定してください。")
        return
    # ... (環境変数の読み込みとクライアント初期化は変更なし) ...
    supabase_client: Client = create_client(supabase_url, supabase_key)

    try:
        # 3. 更新に必要な全プロフィールデータを取得
        print("🔄 全ユーザーのプロフィールを取得中...")
        # IDだけでなく、テキスト生成に必要な全カラムを取得
        response = supabase_client.table('profiles').select("*").execute()
        
        if not response.data:
            print("対象のプロフィールが存在しません。")
            return
            
        profiles: List[dict] = response.data
        print(f"✅ {len(profiles)}件のプロフィールが見つかりました。")

        # 4. 各プロフィールのsearchable_textを計算し、DBを更新
        for profile in track(profiles, description="searchable_textを更新中..."):
            profile_id = profile['id']
            # Python側で検索用テキストを生成
            search_text = create_searchable_text(profile)
            
            # 計算したテキストで、searchable_textカラムを明示的に更新
            supabase_client.table('profiles').update({
                "searchable_text": search_text
            }).eq('id', profile_id).execute()

        print("\n🎉 全てのプロフィールのsearchable_textカラムの更新が完了しました！")

    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()