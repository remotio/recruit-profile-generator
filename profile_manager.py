from typing import List, Dict, Any, Optional
from supabase import Client
import supabase_utils
import ai_utils
import embedding_generator
from typing import List,Dict,Any
from dict_types import UserInput,EditableGeneratedProfile
import uuid
import os
import base64
from pathlib import Path
from typing import Optional



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

    def get_all_profiles(self,current_user_id:Optional[str]=None) -> List[Dict[str, Any]]:
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
            profile=self.get_profile_by_id(user_id)
            return profile is not None
        except ValueError:
            return False

    
    def generate_conversation_starters(self, my_id: str, opponent_id: str) -> Dict[str, List[str]]:
        """
        自分と相手のIDを元に、会話のきっかけを生成する。
        """
        try:
            # 1. データベースから、自分と相手のプロフィール情報を取得する
            #    (self を使って、同じクラス内のメソッドを呼び出します)
            my_profile = self.get_profile_by_id(my_id)
            opponent_profile = self.get_profile_by_id(opponent_id)

            if not my_profile or not opponent_profile:
                return {
                    "common_points": ["エラー：プロフィールの取得に失敗しました。"],
                    "topics": []
                }
            
            # 2. 取得した2つのプロフィール情報を、ai_utilsの関数に渡して、AIに会話のきっかけを生成させる
            conversation_data = ai_utils.create_conversation_starters(my_profile, opponent_profile)

            # 3. AIが生成した結果を、そのまま返す
            return conversation_data
        except Exception as e:
            print(f"会話のきっかけ生成中にエラーが発生しました: {e}")
            raise ValueError("会話のきっかけ生成に失敗しました。") from e

    def get_memo_for_target(self, current_user_id: str, target_user_id: str) -> Dict[str, Any] | None:
        """
        現在ログインしているユーザーが、対象ユーザーについて書いたメモを取得する。
        """
        return supabase_utils.get_memo(self.db_client, current_user_id, target_user_id)
    def save_memo(self,current_user_id:str,target_user_id:str,content:str)->Dict[str,Any]:
        """
        現在ログインしているユーザーが,対象ユーザーについてメモを保存する.

        """
        return supabase_utils.upsert_memo(self.db_client,current_user_id,target_user_id,content)
    def delete_memo(self,current_user_id:str,target_user_id:str)->None:
        """
        現在ログインしているユーザーが，対象ユーザーについて書いたメモを削除する．
        """
        return supabase_utils.delete_memo(self.db_client,current_user_id,target_user_id)
    def upload_profile_image(self,user_id:str,file_body,file_name:str)->str:
        """
        プロフィール画像をSupabase Storageにアップロードし，その公開URLを取得する．
        """

        # 1. 元のファイル名から拡張子（.pngなど）を取得
        _, extension = os.path.splitext(file_name)
        
        # 2. ランダムでユニークなUUIDを生成し，新しいファイル名を作成
        #    例: 123e4567-e89b-12d3-a456-426614174000.png
        safe_file_name = f"{uuid.uuid4()}{extension}"
        
        # 3. public/ユーザID/新しいファイル名 のパスを生成
        file_path = f"{user_id}/{safe_file_name}"

        # supabase_utilsの関数を呼び出し，アップロード&URL取得
        public_url=supabase_utils.upload_file_and_get_url(
            supabase=self.db_client,
            bucket_name="profile_images",
            file_path=file_path,
            file_body=file_body
        )
        return public_url
    def assign_animal_image_url(self,animal_name:str)->str:
        """
        動物名に対応する画像をBase64形式のデータURLで返す．
        """
        try:
            path=Path(f"animal_images/{animal_name}.png")
            if not path.is_file():
                return ""
            with open(path,"rb") as f:
                data=f.read()
            encoded_string=base64.b64encode(data).decode()

            return f"data:image/png;base64,{encoded_string}"
        except Exception as e:
            print(f"画像のBase64エンコード中にエラー: {e}")
            return ""

    def update_profile_image_url(self, user_id: str, public_url: str) -> Dict[str, Any]:
        """
        指定されたユーザーのプロフィール画像URLをデータベースで更新する．
        """
        updated_profile_list = supabase_utils.update_profile_url(self.db_client, user_id, public_url)
        return updated_profile_list[0]
    def search_profiles(self, query: str, current_user_id: Optional[str]) -> List[Dict[str, Any]]:
        """
        プロフィール全体を検索する．
        """
        if not query:
            return []
        
        return supabase_utils.search_profiles(self.db_client, query, current_user_id)