# test_gemini.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    # .envファイルから環境変数を読み込む
    load_dotenv()

    # APIキーを設定
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("エラー: GEMINI_API_KEYが設定されていません。.envファイルを確認してください。")
        return

    genai.configure(api_key=api_key)

    print("Gemini APIに接続中...")

    # 使用するモデルを指定
    model = genai.GenerativeModel('gemini-2.5-flash')

    # テスト用の簡単なプロンプト
    prompt = "キーワード「Python, 読書, 筋トレ」を使って、面白い自己紹介文を100字程度で生成してください。"

    try:
        # APIを呼び出して文章を生成
        response = model.generate_content(prompt)

        print("\n--- 生成された自己紹介文 ---")
        print(response.text)
        print("--------------------------\n")
        print("✅ Gemini APIの連携テストに成功しました！")

    except Exception as e:
        print(f"❌ API呼び出し中にエラーが発生しました: {e}")

if __name__ == "__main__":
    test_gemini_api()