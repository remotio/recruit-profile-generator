import json
import time
import uuid
import os

# JSONファイルのパスを取得
SCRIPT_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_PATH)
JSON_PATH = os.path.join(SCRIPT_DIR, 'dummy_data.json')


def load_dummy_data():
    #dummy_data.jsonからデータを読み込む
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_dummy_data(data):
    #リストをdummy_data.jsonに保存する
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_all_profiles():
    #全ユーザーの一覧を取得する
    all_profiles = load_dummy_data()
    keys_for_list = [
        "profile_id", "nickname", "tags", "university", "department", 
        "profile_image_url", "animal_image_url"
    ]
    return [{key: profile.get(key) for key in keys_for_list} for profile in all_profiles]

def get_profile_by_id(profile_id: str):
    #特定のユーザーの詳細を取得する
    all_profiles = load_dummy_data()
    for profile in all_profiles:
        if profile.get("profile_id") == profile_id:
            return profile
    return None

def create_profile(profile_data: dict):
    #新しいプロフィールを作成し、ファイルに保存する
    hobbies_list = profile_data.get("hobbies", [])
    first_hobby = hobbies_list[0] if hobbies_list else "新しい風を"
    profile_image_url = profile_data.get("profile_image_url") or "https://images.unsplash.com/photo-1599566150163-29194dcaad36?q=80&w=200&h=200&fit=crop"
    
    new_profile = {
        "profile_id": str(uuid.uuid4()),
        "nickname": profile_data.get("nickname"),
        "catchphrase": f"【{first_hobby}】運ぶチャレンジャー】",
        "tags": profile_data.get("tags"),
        "university": profile_data.get("university"),
        "department": profile_data.get("department"),
        "profile_image_url": profile_image_url,
        "animal_image_url": "https://api.dicebear.com/8.x/bottts/svg?seed=new",
        "generated_profile": {
            "catchphrase": f"【{first_hobby}】運ぶチャレンジャー】",
            "basic_info": { "last_name": profile_data.get("last_name"), "first_name": profile_data.get("first_name"), "hometown": profile_data.get("hometown"), "university": profile_data.get("university"), "department": profile_data.get("department"), "birth_date": profile_data.get("birth_date") },
            "talk_topics": { "happy_topic": profile_data.get("happy_topic"), "expert_topic": profile_data.get("expert_topic"), "hobbies": ", ".join(hobbies_list) },
            "introduction_comment": f"はじめまして、{profile_data.get('nickname')}です！{profile_data.get('university')}から来ました。趣味は{', '.join(hobbies_list)}です。よろしくお願いします！",
            "tags": profile_data.get("tags")
        },
        "animal_result": { "name": "ユニコーン", "reason": "新しい可能性を秘めた、ユニークな存在だからです。" }
    }
    
    all_profiles = load_dummy_data()
    all_profiles.append(new_profile)
    save_dummy_data(all_profiles)
    
    time.sleep(1)
    return new_profile


def update_profile(profile_id: str, profile_data: dict):
    """指定されたIDのプロフィールを、提供されたデータで包括的に更新する（全項目対応版）"""
    all_profiles = load_dummy_data()
    
    # 更新対象のプロフィールを検索
    target_profile = None
    for profile in all_profiles:
        if profile.get("profile_id") == profile_id:
            target_profile = profile
            break

    # プロフィールが見つからない場合はNoneを返す
    if not target_profile:
        return None

    # --- ここから更新処理 ---
    
    # 趣味リストを取得し、関連情報を生成
    hobbies_list = profile_data.get("hobbies", target_profile.get("generated_profile", {}).get("talk_topics", {}).get("hobbies", "").split(", "))
    first_hobby = hobbies_list[0] if hobbies_list else "新しい風を"
    
    # 必須項目を更新 (profile_dataにキーがなければ元の値を維持)
    target_profile["nickname"] = profile_data.get("nickname", target_profile.get("nickname"))
    target_profile["tags"] = profile_data.get("tags", target_profile.get("tags"))
    target_profile["university"] = profile_data.get("university", target_profile.get("university"))
    target_profile["department"] = profile_data.get("department", target_profile.get("department"))
    target_profile["profile_image_url"] = profile_data.get("profile_image_url", target_profile.get("profile_image_url"))
    target_profile["animal_image_url"] = profile_data.get("animal_image_url", target_profile.get("animal_image_url"))
    
    # 生成される項目も再生成して更新
    target_profile["catchphrase"] = f"【{first_hobby}】運ぶチャレンジャー】"
    
    # generated_profile の内容を包括的に更新
    target_profile["generated_profile"] = {
        "catchphrase": f"【{first_hobby}】運ぶチャレンジャー】",
        "basic_info": {
            "last_name": profile_data.get("last_name"),
            "first_name": profile_data.get("first_name"),
            "hometown": profile_data.get("hometown"),
            "university": profile_data.get("university"),
            "department": profile_data.get("department"),
            "birth_date": profile_data.get("birth_date")
        },
        "talk_topics": {
            "happy_topic": profile_data.get("happy_topic"),
            "expert_topic": profile_data.get("expert_topic"),
            "hobbies": ", ".join(hobbies_list)
        },
        "introduction_comment": f"はじめまして、{profile_data.get('nickname')}です！{profile_data.get('university')}から来ました。趣味は{', '.join(hobbies_list)}です。よろしくお願いします！",
        "tags": profile_data.get("tags")
    }

    # animal_result の内容を更新
    # animal_resultが編集可能であると仮定
    if "animal_result" in profile_data:
        target_profile["animal_result"] = profile_data.get("animal_result")
    
    # --- 更新処理ここまで ---
    
    # ファイル全体を保存し直す
    save_dummy_data(all_profiles)
    
    # 更新後のプロフィールを返す
    return target_profile
