import google.generativeai as genai
from config import GEMINI_API_KEY
from typing import Dict, Any

# --- 初期設定 ---
# APIキーを設定
genai.configure(api_key=GEMINI_API_KEY)

# 使用するモデルを定義
text_generation_model = genai.GenerativeModel('gemini-1.5-flash')

# --- 関数定義 ---
def generate_introduction_text(profile_data:Dict[str,Any]) -> Dict[str,Any]:
    """
    ユーザの入力を元に，自己紹介文・キャッチフレーズ・タグを生成する．
    @クマペンギン
    雛形を作ったけど間違っているかもしれない．一応調べてみて．

    Args:
        profile_data: ユーザーが入力した情報の辞書．

    Returns:
        AIが生成したテキストを含む辞書．
        例: {
            "catchphrase": "生成されたキャッチフレーズ",
            "introduction_comment": "生成された自己紹介文",
            "generated_tags": "#タグ1 #タグ2" 
        }
    """

    # 1. プロンプトを作成
    prompt=f"""
    ここにプロンプトを書く
    """
    # 2.Gemini APIを呼び出してテキスト生成
    response = text_generation_model.generate_content(prompt)

    # 3.
    # 結果を辞書として返す
    return {} # 仮の戻り値

def classify_animal_type(profile_data:dict[str,Any]) ->Dict[str,str] :
    """
    ユーザーデータと動物の候補リストを元に，最も近い動物タイプを分類し，その理由を生成する．
    @はっぱ
    雛形を作ったけど間違っているかもしれない．一応調べてみて．

    Args:
        profile_data: ユーザーが入力した情報の辞書．
        animal_candidates: 分類の候補となる動物名のリスト．

    Returns:
        分類された動物の名前と，その理由を含む辞書．
        例: {"name": "フクロウ", "reason": "知的な探究心が強いため..."}
    """
    # 1. 動物候補リストを定義
    ANIMAL_CANDIDATES = [
        "ライオン", "フクロウ"
    ]

    # 2. プロンプトを作成
    prompt=f"""
    ここにプロンプトを書く
    """

    # 3. Gemini APIを呼び出して動物タイプを分類
    response = text_generation_model.generate_content(prompt)

    # 4. 結果を辞書として返す
    return {} #仮の戻り値 

def generate_embedding(text: str):
    """
    テキストをベクトル化する
    TODO
    
    """