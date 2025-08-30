from typing import List, Dict, Any, Optional
import supabase_utils
from supabase import Client

class ProfileManager:

    """
    アプリケーションのビジネスロジックを担当するクラス．
    フロントエンドからの要求を受け，supabase_utilsの各関数を呼び出す．
    """
    def __init__(self, supabase_client: Client):
        #各種supabase_utilsの引数となるsupabaseクライアントを保持
        self.db_client = supabase_client
    def create_profile(self,
                       last_name: str,
                       first_name: str,
                       nickname: str,
                       birth_date: str,  # YYYY-MM-DD形式
                       university: str,
                       hometown: str,
                       hobbies: List[str],
                       happy_topic: str,
                       expert_topic: str,
                       tags: List[str]) -> Dict[str, Any]:
        """
        新しいプロフィールを生成して保存する．
        POST /profiles 相当．
        """
        #TODO
        # (実装イメージ)
        # 1. Gemini APIで自己紹介文やキャッチフレーズを生成
        # 2. 引数とAIと生成した内容をあわせてsupabase_utils.add_new_profileでDBに保存
        return {}  # 仮の戻り値

    def update_profile(self,
                       profile_id: str,
                       last_name: str,
                       first_name: str,
                       nickname: str,
                       birth_date: str,  # YYYY-MM-DD形式
                       university: str,
                       hometown: str,
                       hobbies: List[str],
                       happy_topic: str,
                       expert_topic: str,
                       tags: List[str]) -> Dict[str, Any]:
        """
        プロフィール情報を更新する．
        PUT /profiles/{id} 相当．
        profile_idや更新しないフィールドも含めて全てを引数に取る．
        """
        try:
            updated_profile_list = supabase_utils.replace_profile(self.db_client,
                                              {
                                                    "id": profile_id,
                                                    "last_name": last_name,
                                                    "first_name": first_name,
                                                    "nickname": nickname,
                                                    "birth_date": birth_date,
                                                    "university": university,
                                                    "hometown": hometown,
                                                    "hobbies": hobbies,
                                                    "happy_topic": happy_topic,
                                                    "expert_topic": expert_topic,
                                                    "tags": tags
                                                })
            return updated_profile_list[0]
        except Exception as e:
            print(f"プロフィールの更新中にエラーが発生しました: {e}")
            raise ValueError("プロフィールの更新に失敗しました。") from e

    def get_all_profiles(self,current_user_id:str) -> List[Dict[str, Any]]:
        """
        自身を除く全ユーザーの一覧を取得する．
        GET /profiles相当．
        """
        try:
            profiles = supabase_utils.get_all_profiles(self.db_client,current_user_id)
            return profiles
        except ValueError as e:
            print(f"全ユーザーの取得中にエラーが発生しました: {e}")
            raise

    def get_profile_by_id(self, profile_id: str) -> Dict[str, Any]:
        """
        特定のユーザー情報を取得する．
        GET /profiles/{id}相当．
        """
        try:
            profile = supabase_utils.get_profile_by_id(self.db_client, profile_id)
            return profile
        except ValueError as e:
            print(f"プロフィールの取得中にエラーが発生しました: {e}")
            raise

    def find_similar_profiles(self, profile_id: str) -> List[Dict[str, Any]]:
        """
        類似ユーザーを検索する。
        GET /profiles/{id}/similar 相当．
        """
        # (実装イメージ)
        # 1. profile_idを基にユーザーのベクトル(embedding)を取得
        # 2. supabase_utils.find_similar_usersを呼び出す
        return [] # 仮の戻り値