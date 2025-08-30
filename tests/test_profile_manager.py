# tests/test_profile_manager.py
import pytest
from unittest.mock import MagicMock
from profile_manager import ProfileManager

def test_get_profile_by_id_success(mocker):
    """
    正常にプロフィールが取得できる場合のテスト
    """
    # 1. 準備 (Arrange)
    # supabase_utils.get_profile_by_id関数を「偽物（モック）」に置き換える
    mock_supabase_utils = mocker.patch('profile_manager.supabase_utils')
    
    # 偽の関数が返す偽のデータを定義
    fake_profile = {"id": "user-123", "username": "Taro"}
    mock_supabase_utils.get_profile_by_id.return_value = fake_profile
    
    # 偽のDBクライアントと、テスト対象のProfileManagerを作成
    mock_db_client = MagicMock()
    manager = ProfileManager(mock_db_client)
    
    # 2. 実行 (Act)
    result = manager.get_profile_by_id("user-123")
    
    # 3. 検証 (Assert)
    # 偽のDB関数が、正しい引数で1回だけ呼ばれたことを確認
    mock_supabase_utils.get_profile_by_id.assert_called_once_with(mock_db_client, "user-123")
    
    # 戻り値が偽のデータと一致することを確認
    assert result == fake_profile

def test_get_profile_by_id_not_found(mocker):
    """
    プロフィールが見つからなかった場合に、正しくエラーが発生するかのテスト
    """
    # 1. 準備 (Arrange)
    mock_supabase_utils = mocker.patch('profile_manager.supabase_utils')
    # 偽のDB関数がValueErrorを発生するように設定
    mock_supabase_utils.get_profile_by_id.side_effect = ValueError("見つかりませんでした")
    
    mock_db_client = MagicMock()
    manager = ProfileManager(mock_db_client)
    
    # 2. 実行 & 3. 検証 (Act & Assert)
    # manager.get_profile_by_idを呼び出すとValueErrorが発生することを期待
    with pytest.raises(ValueError, match="見つかりませんでした"):
        manager.get_profile_by_id("user-unknown")