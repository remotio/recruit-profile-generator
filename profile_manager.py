from typing import List, Dict, Any, Optional
from supabase import Client
import supabase_utils
import ai_utils
import embedding_generator
from typing import List,Dict,Any
from dict_types import UserInput,EditableGeneratedProfile



class ProfileManager:
    """
    アプリケーションのビジネスロジックを担当するクラス．
    フロントエンドからの要求を受け，supabase_utilsの各関数を呼び出す．
    """
    def __init__(self, supabase_client: Client):
        #各種supabase_utilsの引数となるsupabaseクライアントを保持
        self.db_client = supabase_client

    def create_profile(self, profile_data: UserInput) -> Dict[str, Any]:
        """
        新しいプロフィールを生成して保存する．
        POST /profiles 相当．
        """
        try:
            # AI生成のプロフィールを取得
            ai_text=ai_utils.generate_introduction_text(profile_data)
            animal_type=ai_utils.classify_animal_type(profile_data)
            # AI生成のプロフィールを統合
            intermediate_profile_data={
                **profile_data,
                **ai_text,
                **animal_type
            }  
            # キーワード文書を作成し，ベクトル化
            embedding=embedding_generator.generate_embedding_text(intermediate_profile_data)
            # 最終的なプロフデータを作成
            final_profile_data = {
                **intermediate_profile_data,
                "embedding": embedding
            }
            # 全てのデータをDBに保存
            created_profile_list = supabase_utils.add_new_profile(self.db_client, final_profile_data)
            return created_profile_list[0]
        except Exception as e:
            print(f"プロフィールの作成中にエラーが発生しました: {e}")
            raise ValueError("プロフィールの作成に失敗しました。") from e

    def update_user_input(self,profile_id:str,user_input:UserInput)-> List[Dict[str, Any]]:
        """
            ユーザ入力部分を更新する関数．再度AIによる生成も行う．
        """
        try:
            regenerated_text=ai_utils.generate_introduction_text(user_input)
            new_animal_type=ai_utils.classify_animal_type(user_input)
            profile_for_embedding={
                **user_input,
                **regenerated_text,
                **new_animal_type
            }
            new_embedding=embedding_generator.generate_embedding_text(profile_for_embedding)
            full_profile_data={
                **profile_for_embedding,
                "embedding": new_embedding,
            }
            full_profile_data["id"]=profile_id
            
            updated_profile_list = supabase_utils.replace_profile(self.db_client, full_profile_data)
            return updated_profile_list
        except Exception as e:
            print(f"プロフィールの更新中にエラーが発生しました: {e}")
            raise ValueError("プロフィールの更新に失敗しました。") from e

    def update_generated_profile(self, profile_id: str, profile_data: EditableGeneratedProfile) -> Dict[str, Any]:
        """
            AI生成部分のみを更新する関数．ユーザの変更の上書きを防ぐため，再度AIによる生成は行わない．
        """
        try:
            # DBから既存のプロフィールを取得
            existing_profile=supabase_utils.get_profile_by_id(self.db_client, profile_id)
            # ユーザの編集をマージ
            existing_profile.update(profile_data)
            # 更新されたプロフィールのベクトルを再計算
            new_embedding=embedding_generator.generate_embedding_text(existing_profile)
            # 完全なプロフデータを作成
            full_profile_data = {
                **existing_profile,
                "embedding": new_embedding
            }
            # DBに保存
            updated_profile_list = supabase_utils.replace_profile(self.db_client, full_profile_data)
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
        類似ユーザーを検索する．
        GET /profiles/{id}/similar 相当．
        """
        query_profile=supabase_utils.get_profile_by_id(self.db_client, profile_id)
        if not query_profile or not query_profile.get('embedding'):
            print(f"プロフィールの取得中にエラーが発生しました: embeddingが存在しません")
            raise ValueError("プロフィールの取得に失敗しました。")
        query_vector=query_profile['embedding']
        similar_profiles=supabase_utils.find_similar_users(
            supabase=self.db_client,
            user_id=profile_id,
            query_vector=query_vector
        )
        return similar_profiles
    def sign_up(self,email:str,password:str)->Dict[str,Any]:
        """
        新しいユーザをSupabase Authに登録する．
        また，自動的にログインも行う．
        """
        return supabase_utils.sign_up(self.db_client,email,password)
    def sign_in(self,email:str,password:str)->Dict[str,Any]: 
        """
        ユーザをSupabase Authにログインさせる．
        """
        return supabase_utils.sign_in(self.db_client,email,password)
    def check_profile_exists(self, user_id: str) -> bool:
        """
        プロフィールが存在するか確認する．
        """
        try:
            self.get_profile_by_id(user_id)
            return True
        except ValueError:
            return False
