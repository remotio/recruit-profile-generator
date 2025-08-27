# test_similarity.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client
import time

def run_poc():
    # --- 初期設定 ---
    load_dotenv()
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    embedding_model = "gemini-embedding-001"

    # --- PART 1: 全プロフィールのベクトル化とDBへの保存 ---
    print("--- PART 1: 全プロフィールのベクトル化と保存を開始 ---")
    profiles = supabase.table('profiles').select("id, username, introduction_text").order('id').execute().data

    for profile in profiles:
        print(f"ユーザー「{profile['username']}」のベクトルを生成・保存中...")
        text_to_embed = profile['introduction_text']

        # 「検索対象の文書」としてベクトル化
        response = genai.embed_content(
            model=embedding_model,
            content=text_to_embed,
            task_type="RETRIEVAL_DOCUMENT"
        )
        embedding = response['embedding']

        # Supabaseにベクトルを保存
        supabase.table('profiles').update({'embedding': embedding}).eq('id', profile['id']).execute()

        # レート制限対策
        time.sleep(1)

    print("--- PART 1: 完了 ---")

    # --- PART 2: 特定のユーザーで類似検索を実行 ---
    print("\n--- PART 2: 類似ユーザー検索を開始 ---")

    # 検索の基準となるユーザーを最初のユーザーに設定
    query_profile = profiles[0]
    print(f"検索ユーザー: 「{query_profile['username']}」")

    # 「検索クエリ」としてベクトル化
    response = genai.embed_content(
        model=embedding_model,
        content=query_profile['introduction_text'],
        task_type="RETRIEVAL_QUERY"
    )
    query_embedding = response['embedding']

    # Supabaseの関数を呼び出して検索を実行
    result = supabase.rpc('match_profiles', {
        'query_embedding': query_embedding,
        'match_threshold': 0.7, # 類似度が0.7以上のものを探す
        'match_count': 5        # 最大5件まで（自分自身が最も類似度が高いものとして検出されるので，ほしい数+1を指定する）
    }).execute()

    print("\n--- 検索結果 ---")
    if result.data:
        for match in result.data:
            # 自分自身は結果から除外
            if match['id'] != query_profile['id']:
                print(f"  - ユーザー名: {match['username']} (類似度: {match['similarity']:.4f})")
    else:
        print("類似するユーザーは見つかりませんでした。")


if __name__ == "__main__":
    run_poc()