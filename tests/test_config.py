"""
Test Configuration Manager
"""

import unittest
import tempfile
import os
from src.utils.config import ConfigManager


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        """テスト前の設定"""
        # 一時ファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.config_manager = ConfigManager(self.config_file)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_default_config_loading(self):
        """デフォルト設定の読み込みテスト"""
        self.assertEqual(self.config_manager.get("app.language"), "ja")
        self.assertEqual(self.config_manager.get("battery.low_battery_threshold"), 10)
        self.assertTrue(self.config_manager.get("notifications.enabled"))

    def test_config_set_and_get(self):
        """設定の保存と取得テスト"""
        self.config_manager.set("app.language", "en")
        self.assertEqual(self.config_manager.get("app.language"), "en")

        self.config_manager.set("battery.low_battery_threshold", 15)
        self.assertEqual(self.config_manager.get("battery.low_battery_threshold"), 15)

    def test_battery_threshold_validation(self):
        """バッテリー閾値の検証テスト"""
        # 正常な値
        self.config_manager.set_low_battery_threshold(20)
        self.assertEqual(self.config_manager.get_low_battery_threshold(), 20)

        # 異常な値
        with self.assertRaises(ValueError):
            self.config_manager.set_low_battery_threshold(-1)

        with self.assertRaises(ValueError):
            self.config_manager.set_low_battery_threshold(101)


if __name__ == "__main__":
    unittest.main()
