"""
Logger Setup - ログ管理
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name: str = "Connected", level: int = logging.INFO) -> logging.Logger:
    """ロガーを設定して返す"""
    
    # ログディレクトリの作成
    log_dir = _get_log_directory()
    os.makedirs(log_dir, exist_ok=True)
    
    # ログファイルパス
    log_file = os.path.join(log_dir, f"{name.lower()}.log")
    
    # ロガーの作成
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 既存のハンドラーをクリア（重複を防ぐ）
    if logger.handlers:
        logger.handlers.clear()
    
    # フォーマッターの作成
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ファイルハンドラーの作成（ローテーション付き）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # コンソールハンドラーの作成
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # コンソールは警告以上のみ
    console_handler.setFormatter(formatter)
    
    # ハンドラーをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 親ロガーへの伝播を防ぐ
    logger.propagate = False
    
    logger.info(f"ロガーが初期化されました - ログファイル: {log_file}")
    
    return logger

def _get_log_directory() -> str:
    """ログディレクトリのパスを取得"""
    # ユーザーのAppDataフォルダにログディレクトリを作成
    app_data = os.getenv('APPDATA', os.path.expanduser('~'))
    log_dir = os.path.join(app_data, 'Connected', 'logs')
    return log_dir

def get_logger(name: str = None) -> logging.Logger:
    """既存のロガーを取得（なければ新規作成）"""
    if name is None:
        name = "Connected"
    
    logger = logging.getLogger(name)
    
    # ロガーが設定されていない場合は設定
    if not logger.handlers:
        return setup_logger(name)
    
    return logger

class LogManager:
    """ログ管理クラス"""
    
    def __init__(self):
        self.main_logger = setup_logger("Connected")
        self.bluetooth_logger = setup_logger("Bluetooth")
        self.battery_logger = setup_logger("Battery")
        self.ui_logger = setup_logger("UI")
    
    def get_main_logger(self) -> logging.Logger:
        """メインロガーを取得"""
        return self.main_logger
    
    def get_bluetooth_logger(self) -> logging.Logger:
        """Bluetoothロガーを取得"""
        return self.bluetooth_logger
    
    def get_battery_logger(self) -> logging.Logger:
        """バッテリーロガーを取得"""
        return self.battery_logger
    
    def get_ui_logger(self) -> logging.Logger:
        """UIロガーを取得"""
        return self.ui_logger
    
    def log_system_info(self):
        """システム情報をログに記録"""
        import platform
        import sys
        
        self.main_logger.info("=" * 50)
        self.main_logger.info("Connected アプリケーション開始")
        self.main_logger.info(f"OS: {platform.system()} {platform.release()}")
        self.main_logger.info(f"Python: {sys.version}")
        self.main_logger.info(f"開始時刻: {datetime.now()}")
        self.main_logger.info("=" * 50)
    
    def log_error_with_context(self, logger: logging.Logger, error: Exception, context: str = ""):
        """エラーを詳細情報と共にログに記録"""
        import traceback
        
        logger.error(f"エラーが発生しました: {context}")
        logger.error(f"エラータイプ: {type(error).__name__}")
        logger.error(f"エラーメッセージ: {str(error)}")
        logger.error(f"スタックトレース:\n{traceback.format_exc()}")
    
    def cleanup_old_logs(self, days: int = 30):
        """古いログファイルを削除"""
        import glob
        from datetime import timedelta
        
        log_dir = _get_log_directory()
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # ログファイルパターン
        log_patterns = [
            os.path.join(log_dir, "*.log"),
            os.path.join(log_dir, "*.log.*")
        ]
        
        deleted_count = 0
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                try:
                    file_time = datetime.fromtimestamp(os.path.getctime(log_file))
                    if file_time < cutoff_date:
                        os.remove(log_file)
                        deleted_count += 1
                        self.main_logger.info(f"古いログファイルを削除: {log_file}")
                except Exception as e:
                    self.main_logger.warning(f"ログファイル削除エラー: {log_file} - {e}")
        
        if deleted_count > 0:
            self.main_logger.info(f"{deleted_count}個の古いログファイルを削除しました")
        
        return deleted_count
