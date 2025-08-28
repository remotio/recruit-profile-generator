from supabase import Client

def get_profile_by_id(supabase: Client, user_id: int):
    """
    ユーザーIDを元に，特定のプロフィールをデータベースから取得する．
    一覧ページからプロフィール詳細ページに遷移する際等に使用

    Args:
        supabase: Supabaseクライアントのインスタンス。
        user_id: 取得したいユーザーのID。

    Returns:
        指定されたユーザーのプロフィールデータ。見つからない場合やエラー時はNone。
    """
    try:
        response = supabase.table('profiles').select("*").eq('id', user_id).single().execute()
        return response.data
    except Exception as e:
        print(f"IDによるプロフィール取得中にエラーが発生しました: {e}")
        return None

def add_new_profile(supabase: Client, username: str, answers: dict):
    """
    新しいユーザープロフィールをデータベースに挿入する．
    自己紹介のカラムは空のまま．

    Args:
        supabase: Supabaseクライアントのインスタンス
        username: ユーザー名
        answers: 質問に対するユーザーの回答の辞書 (例: {"hobby": "読書", "skill": "Python"})

    Returns:
        挿入されたデータのリスト，またはエラー時はNone
    """
    try:
        # 挿入するデータを作成．usernameとanswersの内容を結合する．
        new_profile_data = {
            "username": username,
            **answers  # answers辞書を展開して結合
        }

        response = supabase.table('profiles').insert(new_profile_data).execute()
        
        # 挿入されたデータを返す
        return response.data

    except Exception as e:
        print(f"プロフィールの追加中にエラーが発生しました: {e}")
        return None

def update_profile_data(supabase: Client, user_id: int, update_data: dict):
    """
    既存のユーザープロフィールを更新する
    自己紹介文の追加にも利用する

    Args:
        supabase: Supabaseクライアントのインスタンス
        user_id: 更新対象のユーザーID
        update_data: 更新したいデータを含む辞書 (例: {"generated_text": "..."})。

    Returns:
        更新されたデータのリスト，エラー時はNone
    """
    try:
        response = supabase.table('profiles').update(update_data).eq('id', user_id).execute()
        return response.data
    except Exception as e:
        print(f"プロフィールの更新中にエラーが発生しました: {e}")
        return None

def find_similar_users(supabase: Client, user_id: int, query_vector: list):
    """
    指定されたベクトルに類似するユーザーを検索する（自分自身は除外）

    Args:
        supabase: Supabaseクライアントのインスタンス
        user_id: 検索の基となる（そして結果から除外される）ユーザーID
        query_vector: 検索の基準となるベクトルデータ

    Returns:
        類似ユーザーのデータのリスト，エラー時はNone
    """
    try:
        response = supabase.rpc('match_profiles', {
            'query_embedding': query_vector,
            'match_threshold': 0.6,
            'match_count': 10,
            'profile_id_to_exclude': user_id
        }).execute()
        return response.data
    except Exception as e:
        print(f"類似ユーザーの検索中にエラーが発生しました: {e}")
        return None