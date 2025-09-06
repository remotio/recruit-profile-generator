import google.generativeai as genai
import json
from typing import Dict, Any, List
from dict_types import UserInput 
import streamlit as st

# --- 初期設定 ---
# APIキーを安全に読み込む
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
if not GEMINI_API_KEY:
    raise ValueError("エラー: GEMINI_API_KEYが.streamlit/secrets.tomlファイルに設定されていません。")
genai.configure(api_key=GEMINI_API_KEY)

# 使用するモデルを定義
text_generation_model = genai.GenerativeModel('gemini-2.5-flash')

# --- 関数定義 ---
def generate_introduction_text(profile_data: UserInput) -> Dict[str, Any]:
    """
    ユーザの入力を元に，自己紹介文・キャッチフレーズ・タグを生成する．
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
        - "catchphrase": ユーザーの魅力を表す、ユニークなキャッチコピーを、**必ず`【】`（隅付き括弧）で囲んで**生成してください。
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


def classify_animal_type(profile_data: UserInput) -> Dict[str, str]:
    """
    ユーザーデータと動物の候補リストを元に，最も近い動物タイプを分類し，その理由を生成する．

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
        以下のユーザー情報をもとに，次の5カテゴリのいずれかに分類し，
        最も適切な動物を {ANIMAL_CANDIDATES} から1つ選び，理由も述べてください。

        カテゴリ:
        リーダーシップ全開タイプ
        頭脳派・ミステリアスタイプ
        ムードメーカー・元気いっぱいタイプ
        癒し系・ほんわかタイプ
        自由人・マイペースタイプ

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
        ai_response_text = response.text 

        # JSON部分を抜き出す処理
        start_index = ai_response_text.find('{')
        end_index = ai_response_text.rfind('}')
        
        if start_index != -1 and end_index != -1:
            json_string = ai_response_text[start_index : end_index + 1]
            return json.loads(json_string)
        else:
            raise ValueError("AIのレスポンスに有効なJSONが含まれていませんでした。")
    except Exception as e:
        print(f"AIによる動物分類でエラーが発生しました: {e}")
        raise ValueError("動物分類に失敗しました。") from e

def create_conversation_starters(profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    2人のプロフィール情報を元に、会話のきっかけとなる共通点や質問をAIに生成させる。
    @クマペンギン
    """
    
    # 1. 2人のプロフィール情報から、AIに渡すための要約を作成
    your_info = f"""
- ニックネーム: {profile_a.get('nickname')}
- 誕生日: {profile_a.get('birth_date')}
- 大学: {profile_a.get('university')}
- 出身地: {profile_a.get('hometown')}
- 趣味: {', '.join(profile_a.get('hobbies', []))}
- 好きな話題: {profile_a.get('happy_topic')}
- 得意なこと: {profile_a.get('expert_topic')}
- タグ: {', '.join(profile_a.get('tags', []))}
"""

    opponent_info = f"""
- ニックネーム: {profile_b.get('nickname')}
- 誕生日: {profile_b.get('birth_date')}
- 大学: {profile_b.get('university')}
- 出身地: {profile_b.get('hometown')}
- 趣味: {', '.join(profile_b.get('hobbies', []))}
- 好きな話題: {profile_b.get('happy_topic')}
- 得意なこと: {profile_b.get('expert_topic')}
- タグ: {', '.join(profile_b.get('tags', []))}
"""

    # 2. プロンプトを作成
    prompt = f"""
# あなたへの役割
あなたは、初対面の二人が仲良くなるための会話をサポートする、優れたアイスブレイク・アシスタントです。

# 2人のプロフィール情報
## あなた（ユーザーA）
{your_info}

## 相手（ユーザーB）
{opponent_info}

# 命令
上記の2人のプロフィールを比較し、「あなた」が「相手」と楽しく会話を始めるための「きっかけ」を生成してください。
- "common_points": 「あなた」と「相手」のプロフィールから、**会話のきっかけとして面白い、ユニークな共通点**を3つまで、**短い単語やフレーズ**で挙げてください。
- **【重要】以下の当たり前の共通点は除外してください：**
  - 年齢が近いこと
  - 学生であること
  - （今回の集まりの）内定者であること
- 表面的な一致だけでなく、地理的（例：関西出身）、カテゴリ的（例：インドアな趣味）など、**より深いレベルでの意外な共通点**を優先してください。共通点がない場合は、その旨を正直に記載してください。
- "topics": 「あなた」が「相手」に質問するための、具体的で面白い話題を3つ提案してください。提案は必ず「相手の〇〇について、△△と質問してみましょう。」というアドバイス形式で、あなた（ユーザーA）へのメッセージとして作成してください。提案文の中では、相手のニックネームを直接使わないでください。

# 出力形式
必ず、以下の例のようなJSON形式で出力してください。
{{
  "common_points": [
    "福岡県出身",
    "映画鑑賞が趣味",
    "九州地方の大学"
  ],
  "topics": [
    "相手の趣味である「カフェ巡り」について、「普段はどんなカフェに行かれるんですか？」と質問してみましょう。",
    "出身地が同じ福岡県なので、「福岡で一番好きなラーメン屋さんはどこですか？」と聞いてみるのはどうでしょう。",
    "相手はコーヒーの淹れ方が得意とのことなので、「おすすめの豆や淹れ方をぜひ教えてほしいです！」とお願いしてみましょう。"
  ]
}}
"""
    
    try:
        # 3. Gemini APIを呼び出してテキスト生成
        # 応答時間の関係で，1.5-flashを使用
        conv_starter_model = genai.GenerativeModel('gemini-2.5-flash')
        response = conv_starter_model.generate_content(prompt)
        ai_response_text = response.text
        
        # 4. AIの返事からJSON部分だけを賢く抜き出す
        start_index = ai_response_text.find('{')
        end_index = ai_response_text.rfind('}')
        
        if start_index != -1 and end_index != -1:
            json_string = ai_response_text[start_index : end_index + 1]
            ai_response_dict = json.loads(json_string)
            return ai_response_dict
        else:
            raise ValueError("AIのレスポンスに有効なJSONが含まれていません。")

    except Exception as e:
        print(f"会話のきっかけ生成でエラーが発生しました: {e}")
        raise ValueError("会話のきっかけ生成に失敗しました。") from e

# --- ここからがテスト用のコードです ---
if __name__ == '__main__':
    # --- テスト1: 自己紹介文の生成 ---
    print("--- Test 1: 自己紹介文の生成を開始します... ---")
    test_user_input_saki = {
        "last_name": "山田", "first_name": "さき", "nickname": "さき",
        "birth_date": "2002-08-10", "university": "福岡大学", "hometown": "福岡県",
        "hobbies": ["カフェ巡り", "映画鑑賞"], "happy_topic": "おすすめの映画について",
        "expert_topic": "美味しいコーヒーの淹れ方"
    }
    generated_data = generate_introduction_text(test_user_input_saki)
    print("\n--- AIからのレスポンス (自己紹介文) ---")
    import pprint
    pprint.pprint(generated_data)
    print("-" * 30)
    
    # 2. 動物分類のテストを追加
    print("--- AIに動物分類をリクエストします... ---")
    animal_data = classify_animal_type(test_user_input)
    pprint.pprint(animal_data)
    print("--------------------------")

    # --- テスト3: 会話のきっかけ生成 ---
    print("\n--- Test 3: 会話のきっかけ生成を開始します... ---")
    # 2人目のテストユーザーを定義
    test_user_input_rimo = {
        "last_name": "鈴木", "first_name": "りも", "nickname": "りも",
        "birth_date": "2001-05-20", "university": "東京工業大学", "hometown": "東京都",
        "hobbies": ["プログラミング", "音楽フェス"], "happy_topic": "新しい技術について",
        "expert_topic": "インフラ構築", "tags": ["#Supabase", "#音楽好き"]
    }
    
    # 新しい関数を呼び出す
    conversation_starters = create_conversation_starters(test_user_input_saki, test_user_input_rimo)
    print("\n--- AIからのレスポンス (会話のきっかけ) ---")
    pprint.pprint(conversation_starters)
    print("-" * 30)
