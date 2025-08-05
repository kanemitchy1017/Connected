"""
Configuration Manager - 設定管理
"""

import json
import os
import logging
from typing import Dict, Any, Optional

class ConfigManager:
    """アプリケーション設定管理クラス"""
    
    def __init__(self, config_file: str = "config.json"):
        self.logger = logging.getLogger(__name__)
        self.config_file = self._get_config_path(config_file)
        self.config_data = self._load_default_config()
        self.load_config()
    
    def _get_config_path(self, filename: str) -> str:
        """設定ファイルのパスを取得"""
        # ユーザーのAppDataフォルダに設定ファイルを保存
        app_data = os.getenv('APPDATA', os.path.expanduser('~'))
        config_dir = os.path.join(app_data, 'Connected')
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(config_dir, exist_ok=True)
        
        return os.path.join(config_dir, filename)
    
    def _load_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を読み込み"""
        return {
            "app": {
                "language": "ja",
                "theme": "system",  # system, light, dark
                "start_with_windows": False,
                "minimize_to_tray": True
            },
            "battery": {
                "low_battery_threshold": 10,
                "critical_battery_threshold": 5,
                "update_interval": 60,  # 秒
                "show_percentage": True,
                "show_icon": True
            },
            "notifications": {
                "enabled": True,
                "low_battery_alert": True,
                "critical_battery_alert": True,
                "device_connection_alert": False,
                "sound_enabled": True,
                "duration": 5  # 秒
            },
            "devices": {
                "auto_detect": True,
                "supported_types": ["earphones", "headphones", "mouse", "keyboard"],
                "device_specific_thresholds": {}  # device_address: threshold
            },
            "ui": {
                "window_position": {"x": 100, "y": 100},
                "window_size": {"width": 400, "height": 300},
                "always_on_top": False,
                "show_in_taskbar": False
            }
        }
    
    def load_config(self):
        """設定ファイルから設定を読み込み"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # デフォルト設定と読み込んだ設定をマージ
                    self.config_data = self._merge_config(self.config_data, loaded_config)
                    self.logger.info(f"設定ファイルを読み込みました: {self.config_file}")
            else:
                self.logger.info("設定ファイルが見つかりません。デフォルト設定を使用します。")
                self.save_config()  # デフォルト設定を保存
        except Exception as e:
            self.logger.error(f"設定ファイルの読み込みエラー: {e}")
            self.logger.info("デフォルト設定を使用します。")
    
    def save_config(self):
        """設定をファイルに保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"設定ファイルを保存しました: {self.config_file}")
        except Exception as e:
            self.logger.error(f"設定ファイルの保存エラー: {e}")
    
    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """デフォルト設定と読み込み設定をマージ"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_config(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """設定値を取得 (例: "app.language")"""
        try:
            keys = key_path.split('.')
            value = self.config_data
            
            for key in keys:
                value = value[key]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """設定値を設定 (例: "app.language", "en")"""
        try:
            keys = key_path.split('.')
            config = self.config_data
            
            # 最後のキー以外まで移動
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            
            # 値を設定
            config[keys[-1]] = value
            
            # 自動保存
            self.save_config()
            
        except Exception as e:
            self.logger.error(f"設定値の設定エラー: {e}")
    
    def get_low_battery_threshold(self) -> int:
        """低バッテリー閾値を取得"""
        return self.get("battery.low_battery_threshold", 10)
    
    def set_low_battery_threshold(self, threshold: int):
        """低バッテリー閾値を設定"""
        if 0 <= threshold <= 100:
            self.set("battery.low_battery_threshold", threshold)
        else:
            raise ValueError("閾値は0から100の間で設定してください")
    
    def get_update_interval(self) -> int:
        """更新間隔を取得（秒）"""
        return self.get("battery.update_interval", 60)
    
    def set_update_interval(self, seconds: int):
        """更新間隔を設定"""
        if seconds >= 10:  # 最低10秒
            self.set("battery.update_interval", seconds)
        else:
            raise ValueError("更新間隔は10秒以上で設定してください")
    
    def is_notifications_enabled(self) -> bool:
        """通知が有効かどうか"""
        return self.get("notifications.enabled", True)
    
    def get_language(self) -> str:
        """言語設定を取得"""
        return self.get("app.language", "ja")
    
    def get_theme(self) -> str:
        """テーマ設定を取得"""
        return self.get("app.theme", "system")
    
    def reset_to_defaults(self):
        """設定をデフォルトにリセット"""
        self.config_data = self._load_default_config()
        self.save_config()
        self.logger.info("設定をデフォルトにリセットしました")
