import os
import google.generativeai as genai
from typing import Dict, Any, List

# Gemini APIキーの設定
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
EMBEDDING_MODEL = "gemini-embedding-001"

def create_keywords(profile_data: Dict[str, Any]) -> str:
    """プロフィールデータから検索用のキーワード文書を生成する"""
    keywords = []
    keywords.extend(profile_data.get("hobbies", []))
    
    # tagsがリスト形式でも文字列形式でも対応できるようにする
    tags = profile_data.get("tags", [])
    if isinstance(tags, str):
        tags = tags.replace("#", "").split()
    keywords.extend(tags)
    
    keywords.append(profile_data.get("expert_topic", ""))
    keywords.append(profile_data.get("happy_topic", ""))
    keywords.append(profile_data.get("hometown", ""))
    
    final_keywords = [word for word in keywords if word]
    return " ".join(final_keywords)

def generate_embedding_text(profile_data: Dict[str, Any]) -> List[float]:
    """
    検索「対象文書」用のベクトルを生成する。
    （データベースに保存する全ユーザーのプロフィールはこちらを使う）
    """
    keyword_document = create_keywords(profile_data)
    
    if not keyword_document:
        return [] # キーワードが空の場合は空のリストを返す

    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=keyword_document,
        task_type="RETRIEVAL_DOCUMENT"
    )
    return response['embedding']

def generate_embedding_query(profile_data: Dict[str, Any]) -> List[float]:
    """
    検索「クエリ」用のベクトルを生成する。
    （検索の基準となる一人のユーザーはこちらを使う）
    """
    keyword_document = create_keywords(profile_data)

    if not keyword_document:
        return []

    response = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=keyword_document,
        task_type="RETRIEVAL_QUERY"
    )
    return response['embedding']