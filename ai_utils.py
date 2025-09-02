import google.generativeai as genai
import json
import os  # osを追加
from dotenv import load_dotenv  # dotenvを追加
from typing import Dict, Any, List
from dict_types import UserInput 

# .envファイルから環境変数を読み込む
load_dotenv()

# --- 初期設定 ---
# os.getenvを使って.envファイルからAPIキーを安全に読み込む
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("エラー: GEMINI_API_KEYが.envファイルに設定されていません。")
genai.configure(api_key=GEMINI_API_KEY)

# 使用するモデルを定義
text_generation_model = genai.GenerativeModel('gemini-2.5-flash')

# --- 関数定義 ---
def generate_introduction_text(profile_data: UserInput) -> Dict[str, Any]:
    """
    ユーザの入力を元に，自己紹介文・キャッチフレーズ・タグを生成する．
    @クマペンギン
    """
    
    # 1. プロンプトを完成させる
    prompt = f"""
# あなたへの役割
あなたは、プロのプロフィールライターです。与えられた簡単なアンケート結果から、その人の魅力や個性が最大限に引き出され、初対面でも会話が弾むような、親しみやすい自己紹介カードを作成するのがあなたの仕事です。

# ユーザー情報
- ニックネーム: {profile_data['nickname']}
- 生年月日: {profile_data['birth_date']}
- 出身大学: {profile_data['university']}
- 出身地: {profile_data['hometown']}
- 趣味や好きなこと: {', '.join(profile_data['hobbies'])}
- 話しかけられるなら、どんな話題が一番嬉しいですか？: {profile_data['happy_topic']}
- 「実は、〇〇にはちょっと詳しいです！」と自慢できることは何ですか？: {profile_data['expert_topic']}

# 命令
上記のユーザー情報を元に、あなたのライターとしてのセンスを最大限に発揮し、以下のキーを持つJSONオブジェクトを生成してください。
- "catchphrase": ユーザーの魅力を表す、ユニークなキャッチコピーを生成してください。
- "introduction_text": 本人が語っているような、自然な一人称の自己紹介文（ですます調）を生成してください。
- "tags": 会話のきっかけになりそうなキーワードを3つ抽出し、文字列の配列（リスト）として生成してください。

# 出力形式
必ず、以下の例のようなJSON形式で出力してください。
{{
  "catchphrase": "【一杯のコーヒーから物語を紡ぐ、シネマティック・トラベラー】",
  "introduction_text": "はじめまして、さきです！休日はカフェでのんびりしたり...",
  "tags": ["#カフェ部", "#映画好きと繋がりたい", "#ハンドドリップ派"]
}}
"""
    
    try:
        # 2. Gemini APIを呼び出してテキスト生成
        response = text_generation_model.generate_content(prompt)
        ai_response_text = response.text
        
        # 3. AIの返事からJSON部分だけを賢く抜き出す
        start_index = ai_response_text.find('{')
        end_index = ai_response_text.rfind('}')
        
        if start_index != -1 and end_index != -1:
            json_string = ai_response_text[start_index : end_index + 1]
            # 4. 文字列をPythonの辞書に「翻訳」する
            ai_response_dict = json.loads(json_string)
            # 5. 本物のAIの生成結果を返す
            return ai_response_dict
        else:
            # AIの返事にJSONが見つからなかった場合、エラーを発生させる
            raise ValueError("AIのレスポンスに有効なJSONが含まれていません。")

    except Exception as e:
        print(f"AIによるテキスト生成でエラーが発生しました: {e}")
        # エラーが発生した場合は、失敗したことが分かる情報を返す
        return {
            "catchphrase": "エラー：キャッチコピーの生成に失敗",
            "introduction_text": f"自己紹介文の生成に失敗しました。エラー内容: {e}",
            "tags": []
        }

# --- ここからがテスト用のコードです ---
if __name__ == '__main__':
    # 1. テスト用のダミーデータを作成する
    # このデータは、りもさんが定義したUserInputの型に合わせて作ります。
    test_user_input: UserInput = {
        "last_name": "山田",
        "first_name": "さき",
        "nickname": "さき",
        "birth_date": "2002-08-10",
        "university": "福岡大学",
        "hometown": "福岡県",
        "hobbies": ["カフェ巡り", "映画鑑賞"],
        "happy_topic": "おすすめの映画について",
        "expert_topic": "美味しいコーヒーの淹れ方",
    }

    # 2. 作成した関数を呼び出してみる
    print("--- AIに自己紹介文の生成をリクエストします... ---")
    generated_data = generate_introduction_text(test_user_input)

    # 3. 結果をコンソールに分かりやすく表示する
    print("\n--- AIからのレスポンス ---")
    import pprint
    pprint.pprint(generated_data)
    print("--------------------------")

    # 4. 取得したデータを使ってみる（シミュレーション）
    if generated_data and "catchphrase" in generated_data:
        print(f"\n生成されたキャッチコピー: {generated_data['catchphrase']}")

def classify_animal_type(profile_data: UserInput) -> Dict[str, str]:
    """
    ユーザーデータと動物の候補リストを元に，最も近い動物タイプを分類し，その理由を生成する．
    @はっぱ
    雛形を作ったけど間違っているかもしれない．一応調べてみて．

    Args:
        profile_data: ユーザーが入力した情報の辞書．
        animal_candidates: 分類の候補となる動物名のリスト．

    Returns:
        分類された動物の名前と，その理由を含む辞書．
        例: {"animal_name": "フクロウ", "animal_reason": "知的な探究心が強いため..."}
    """
    # 1. 動物候補リストを定義
    ANIMAL_CANDIDATES = [
         "ライオン", "トラ", "ワシ", "馬", "オオカミ",
        "フクロウ", "イルカ", "ネコ", "カラス", "タカ",
        "犬", "サル", "ペンギン", "カメ", "カンガルー",
        "ウサギ", "コアラ", "パンダ", "羊", "カワウソ"
    ]

    # 2. プロンプトを作成
    prompt=f"""
    ここにプロンプトを書く
       以下のユーザー情報をもとに，次の5カテゴリのいずれかに分類し，
    最も適切な動物を {ANIMAL_CANDIDATES} から1つ選び，理由も述べてください。

    カテゴリ:
    1. リーダーシップ全開タイプ
    2. 頭脳派・ミステリアスタイプ
    3. ムードメーカー・元気いっぱいタイプ
    4. 癒し系・ほんわかタイプ
    5. 自由人・マイペースタイプ

    出力形式は必ずJSONで:
    {{
        "animal_name": "...",
        "animal_category": "...",
        "animal_reason": "..."
    }}

    ユーザー情報: {profile_data}

    """

     try:
        response = text_generation_model.generate_content(prompt)
        text = response.candidates[0].content.parts[0].text

        import json
        return json.loads(text)
    except Exception as e:
        return {"error": "動物分類に失敗しました"}


# --- テスト用コード ---

if __name__ == "__main__":
    # --- ダミーデータを用意 ---
    dummy_profile_1 = {
        "name": "太郎",
        "hobby": "読書と映画鑑賞",
        "personality": "落ち着いていて分析好き",
        "strength": "集中力が高い",
        "weakness": "運動は苦手"
    }

    dummy_profile_2 = {
        "name": "花子",
        "hobby": "友達と遊ぶことと旅行",
        "personality": "明るくておしゃべり好き",
        "strength": "誰とでもすぐ仲良くなれる",
        "weakness": "ちょっとせっかち"
    }

    # --- テスト実行 ---
    print("=== 自己紹介生成テスト ===")
    print(generate_introduction_text(dummy_profile_1))
    print(generate_introduction_text(dummy_profile_2))

    print("\n=== 動物分類テスト ===")
    print(classify_animal_type(dummy_profile_1))
    print(classify_animal_type(dummy_profile_2))

