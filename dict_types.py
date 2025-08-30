from typing import TypedDict,List,Dict,Any

class UserInput(TypedDict):
    """
        ユーザーが新規作成時に入力するデータ形式の辞書の定義
    """
    last_name: str
    first_name: str
    nickname: str
    birth_date: str  # YYYY-MM-DD形式
    university: str
    hometown: str
    hobbies: List[str]
    happy_topic: str
    expert_topic: str
class EditableGeneratedProfile(TypedDict):
    """
        ユーザーが編集可能なAI生成による項目の辞書の定義,
    """
    introduction_text: str
    catchphrase: str
    tags: List[str]
class FullUserProfile(UserInput,EditableGeneratedProfile):
    """
        ユーザーのプロフィール情報を全て含む辞書の定義，
        UserInput 及び EditableGeneratedProfile を継承している
    """
    id: str
    created_at: str
    animal_name: str
    animal_reason: str
    embedding: List[float]