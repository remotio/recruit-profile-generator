from supabase import Client
from typing import Dict, Any, List

def get_profile_by_id(supabase: Client, profile_id: str):
    """
    ユーザーIDを元に，特定のプロフィールをデータベースから取得する．
    一覧ページからプロフィール詳細ページに遷移する際等に使用

    Args:
        supabase: Supabaseクライアントのインスタンス．
        profile_id: 取得したいユーザのID．

    Returns:
        指定されたユーザーのプロフィールデータ．
    """
    try:
        response = supabase.table('profiles').select("*").eq('id', profile_id).single().execute()
        if not response.data:
            raise ValueError(f"ID {profile_id} のプロフィールが見つかりませんでした。")
        return response.data
    except Exception as e:
        print(f"データベースへのアクセス中にエラーが発生しました。: {e}")
        raise ValueError("データベースへのアクセス中にエラーが発生しました。") from e

def add_new_profile(supabase: Client, profile_data: Dict[str, Any]):
    """
    新しいユーザープロフィールをデータベースに挿入する．

    Args:
        supabase: Supabaseクライアントのインスタンス
        profile_data: プロフィールに必要な項目が揃った新しいプロフィールデータ（Supabaseの関数の作法で辞書型だが，1人分のデータを想定）

    Returns:
        挿入されたデータのリスト
    """
    try:
        response=supabase.table('profiles').insert([profile_data]).execute()

        if not response.data:
            raise ValueError("プロフィールの追加に失敗しました。")
        return response.data
    except Exception as e:
        print(f"プロフィールの追加中にエラーが発生しました: {e}")
        raise ValueError("プロフィールの追加中にエラーが発生しました。") from e

def replace_profile(supabase: Client, profile_data: Dict[str, Any]):
    """
    プロフィール情報全体を新しいデータで置き換える．
    PUT /profiles/{id} 相当．

    Args:
        supabase: Supabaseクライアントのインスタンス
        profile_data: プロフィールに必要な項目が揃った更新後のプロフィールデータ（Supabaseの関数の作法で辞書型だが，1人分のデータを想定）
    Returns:
        置き換えられたデータのリスト
    """
    try:
        response = supabase.table('profiles').upsert([profile_data], on_conflict='id').execute()
        if not response.data:
            raise ValueError("プロフィールの更新に失敗しました。")
        return response.data
    except Exception as e:
        print(f"プロフィールの更新中にエラーが発生しました: {e}")
        raise ValueError("プロフィールの更新中にエラーが発生しました。") from e

def find_similar_users(supabase: Client, user_id: str, query_vector: list):
    """
    指定されたベクトルに類似するユーザーを検索する（自分自身は除外）

    Args:
        supabase: Supabaseクライアントのインスタンス
        user_id: 検索の基となる（そして結果から除外される）ユーザーID
        query_vector: 検索の基準となるベクトルデータ

    Returns:
        類似ユーザーのデータのリスト
    """
    try:
        response = supabase.rpc('match_profiles', {
            'query_embedding': query_vector,
            'match_threshold': 0.6,
            'match_count': 10,
            'profile_id_to_exclude': user_id
        }).execute()
        if not response.data:
            print("類似ユーザーが見つかりませんでした。")
            return []
        return response.data
    except Exception as e:
        print(f"類似ユーザーの検索中にエラーが発生しました: {e}")
        raise ValueError("類似ユーザーの検索中にエラーが発生しました。") from e
    
def get_all_profiles(supabase: Client,user_id:str):
    """
    自身を除く全ユーザーのプロフィールを取得する．

    Args:
        supabase: Supabaseクライアントのインスタンス．
        user_id: 自身のユーザーID（結果から除外するために使用）．

    Returns:
        ユーザーのプロフィールデータのリスト
    """
    try:
        response = supabase.table('profiles').select("*").neq('id', user_id).execute()
        if not response.data:
            return [] #自分以外のユーザが存在しない場合は空リストを返す 
        return response.data
    except Exception as e:
        print(f"全ユーザーの取得中にエラーが発生しました: {e}")
        raise ValueError("全ユーザーの取得中にエラーが発生しました。") from e
def update_profile_embedding(supabase: Client, profile_id: str, embedding: list):
    """
    指定されたユーザーのプロフィールにベクトルデータを更新する．

    Args:
        supabase: Supabaseクライアントのインスタンス
        profile_id: ベクトルを更新したいユーザーのID
        embedding: 新しいベクトルデータ

    Returns:
        更新されたプロフィールデータ
    """
    try:
        response = supabase.table('profiles').update({'embedding': embedding}).eq('id', profile_id).execute()
        if not response.data:
            raise ValueError("プロフィールのベクトル更新に失敗しました。")
        return response.data
    except Exception as e:
        print(f"プロフィールのベクトル更新中にエラーが発生しました: {e}")
        raise ValueError("プロフィールのベクトル更新中にエラーが発生しました。") from e
def sign_up(supabase:Client,email:str,password:str)->Dict[str,Any]:
    """
    新しいユーザをSupabase Authに登録する．
    """
    try:
        response=supabase.auth.sign_up({
            "email":email,
            "password":password
        })
        if response.user is None:
            raise ValueError("新規登録に失敗しました。")
        return {
            "id":response.user.id,
            "email":response.user.email
        }
    except Exception as e:
        # メールの重複によるエラーをチェック
        if "already registered" in str(e):
            raise ValueError("このメールアドレスは既に登録されています。") from e
        elif "Password should be at least 6 characters." in str(e):
            raise ValueError("パスワードは6文字以上である必要があります。") from e
        elif "Invalid email" in str(e):
            raise ValueError("メールアドレスの形式が正しくありません。") from e
    
        else:
            print(f"新規登録中にエラーが発生しました: {e}")
            raise ValueError("新規登録に失敗しました。") from e

def sign_in(supabase:Client,email:str,password:str)->Dict[str,Any]:
    """
    Supabase Authでユーザにサインインさせる．
    """
    try:
        response=supabase.auth.sign_in_with_password({
            "email":email,
            "password":password
        })
        if response.user is None:
            raise ValueError("ログインに失敗しました。")
        return {
            "id":response.user.id,
            "email":response.user.email
        }
    except Exception as e:
        print(f"ログイン中にエラーが発生しました: {e}")
        raise ValueError("ログインに失敗しました。") from e
def get_memo(supabase: Client, author_id: str, target_id: str) -> Dict[str, Any] | None:
    """
    特定の一人のユーザーが，別のユーザーについて書いたメモを取得する．
    メモが存在しない場合はNoneを返す．
    """
    try:
        response = supabase.table('memos').select("*") \
            .eq('author_id', author_id) \
            .eq('target_id', target_id) \
            .execute()

        # 結果のリストにデータが含まれていれば，最初の要素（辞書）を返す
        if response.data:
            return response.data[0]
        # データがなければ（メモが存在しなければ）Noneを返す
        else:
            return None
            
    except Exception as e:
        print(f"メモの取得中にエラーが発生しました: {e}")
        raise ValueError("メモの取得中にエラーが発生しました。") from e
def upsert_memo(supabase:Client,author_id:str,target_id:str,memo_text:str)->Dict[str,Any]:
    """
    author_idからtarget_idへのメモを追加または更新する．
    """
    try:
        response=supabase.table('memos').upsert({
            "author_id":author_id,
            "target_id":target_id,
            "content":memo_text
        },on_conflict='author_id,target_id').execute()
        if not response.data:
            raise ValueError("メモの追加または更新に失敗しました。")
        return response.data[0]# upsertはリストを返すため最初の要素を取得
    except Exception as e:
        print(f"メモの追加または更新中にエラーが発生しました: {e}")
        raise ValueError("メモの追加または更新に失敗しました。") from e
def delete_memo(supabase:Client,author_id:str,target_id:str)->None:
    """
    メモを削除する
    """
    try:
        supabase.table('memos').delete().eq('author_id',author_id).eq('target_id',target_id).execute()
    except Exception as e:
        print(f"メモの削除中にエラーが発生しました: {e}")
        raise ValueError("メモの削除に失敗しました。") from e
def upload_file_and_get_url(supabase:Client,bucket_name:str,file_path:str,file_body:bytes)->str:
    """
    指定されたバケットにファイルをアップロードし、その公開URLを取得する。

    Args:
        supabase: Supabaseクライアントのインスタンス
        bucket_name: ファイルをアップロードするバケットの名前
        file_path: バケット内でのファイルのパス（例: "images/photo.jpg"）
        file_data: アップロードするファイルのバイナリデータ

    Returns:
        アップロードされたファイルの公開URL
    """
    try:
        # ファイルをアップロード
        response = supabase.storage.from_(bucket_name).upload(file=file_body, path=file_path)
        # アップロードしたファイルの公開URLを取得
        response=supabase.storage.from_(bucket_name).get_public_url(file_path)
        return response
    except Exception as e:
        print(f"ファイルのアップロード中にエラーが発生しました: {e}")
        raise ValueError("ファイルのアップロードに失敗しました。") from e


