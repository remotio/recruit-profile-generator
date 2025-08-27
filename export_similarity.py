# export_similarity.py (非対称検索バージョン)
import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client
import pandas as pd
import time

def export_asymmetric_similarity():
    # --- 初期設定 ---
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    embedding_model = "gemini-embedding-001"
    
    print("Supabaseから全ユーザーのプロフィールを取得中...")
    
    try:
        # まず、全ユーザーの情報を取得
        profiles_res = supabase.table('profiles').select("id, username, introduction_text").order('id').execute()
        profiles = profiles_res.data

        if not profiles:
            print("エラー: プロフィールが見つかりません。")
            return

        all_similarity_data = []

        # --- 各ユーザーを「検索者」としてループ処理 ---
        for query_profile in profiles:
            query_username = query_profile['username']
            print(f"「{query_username}」を検索者として類似度を計算中...")

            # 「検索クエリ」としてベクトル化
            response = genai.embed_content(
                model=embedding_model,
                content=query_profile['introduction_text'],
                task_type="RETRIEVAL_QUERY"
            )
            query_embedding = response['embedding']
            
            # Supabaseの関数を呼び出して、全ユーザーとの類似度を検索
            # match_countを多めに、match_thresholdを低くして全ペアを取得
            result = supabase.rpc('match_profiles', {
                'query_embedding': query_embedding,
                'match_threshold': 0.0, 
                'match_count': 100 
            }).execute()
            
            # 結果をリストに追加
            for match in result.data:
                all_similarity_data.append({
                    'username_1': query_username,
                    'username_2': match['username'],
                    'similarity': match['similarity']
                })
            
            # レート制限対策
            print("  -> 1秒待機...")
            time.sleep(1)

        print("\nデータをCSV用の表形式に加工中...")
        
        # 取得した全データをDataFrameに変換
        df = pd.DataFrame(all_similarity_data)

        # DataFrameをピボットして、ユーザー名をインデックスとカラムにした表を作成
        similarity_matrix = df.pivot(
            index='username_1',
            columns='username_2',
            values='similarity'
        )

        # CSVファイルとして出力
        csv_filename = "similarity_matrix_asymmetric.csv"
        similarity_matrix.to_csv(csv_filename, encoding='cp932')

        print(f"\n✅✅✅ 成功！ ✅✅✅")
        print(f"非対称検索での類似度マトリックスを '{csv_filename}' に出力しました。")

    except Exception as e:
        print(f"❌ 処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    export_asymmetric_similarity()