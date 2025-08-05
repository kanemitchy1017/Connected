"""
Notification Manager - 通知機能
"""

import logging
from plyer import notification
from PyQt5.QtWidgets import QSystemTrayIcon, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal

class NotificationManager(QObject):
    """通知管理クラス"""
    
    # シグナル定義
    notification_sent = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.notification_enabled = True
    
    def send_notification(self, title: str, message: str, duration: int = 5):
        """システム通知を送信"""
        if not self.notification_enabled:
            return
        
        try:
            # Windows 10/11のネイティブ通知を使用
            notification.notify(
                title=title,
                message=message,
                app_name="Connected",
                timeout=duration,
                toast=True  # Windows 10/11のトースト通知
            )
            
            self.logger.info(f"通知送信: {title} - {message}")
            self.notification_sent.emit(title, message)
            
        except Exception as e:
            self.logger.error(f"通知送信エラー: {e}")
            # フォールバック: システムトレイ通知
            self._fallback_tray_notification(title, message)
    
    def _fallback_tray_notification(self, title: str, message: str):
        """システムトレイ通知へのフォールバック"""
        try:
            # システムトレイアイコンからの通知
            # 実際の実装では、メインアプリケーションのトレイアイコンインスタンスを使用
            pass
        except Exception as e:
            self.logger.error(f"フォールバック通知エラー: {e}")
    
    def send_battery_alert(self, device_name: str, battery_level: int):
        """バッテリーアラート専用の通知"""
        if battery_level <= 5:
            title = "🔋 緊急: バッテリー残量極少"
            message = f"{device_name}のバッテリーが{battery_level}%です。すぐに充電してください。"
        elif battery_level <= 10:
            title = "⚠️ 警告: バッテリー残量低下"
            message = f"{device_name}のバッテリーが{battery_level}%になりました。充電をお勧めします。"
        elif battery_level <= 20:
            title = "📱 お知らせ: バッテリー残量注意"
            message = f"{device_name}のバッテリーが{battery_level}%です。"
        else:
            return  # 20%以上の場合は通知しない
        
        self.send_notification(title, message)
    
    def send_device_connected(self, device_name: str):
        """デバイス接続通知"""
        title = "🔗 デバイス接続"
        message = f"{device_name}が接続されました"
        self.send_notification(title, message, duration=3)
    
    def send_device_disconnected(self, device_name: str):
        """デバイス切断通知"""
        title = "🔌 デバイス切断"
        message = f"{device_name}が切断されました"
        self.send_notification(title, message, duration=3)
    
    def enable_notifications(self):
        """通知を有効にする"""
        self.notification_enabled = True
        self.logger.info("通知が有効になりました")
    
    def disable_notifications(self):
        """通知を無効にする"""
        self.notification_enabled = False
        self.logger.info("通知が無効になりました")
    
    def is_notification_enabled(self) -> bool:
        """通知が有効かどうかを確認"""
        return self.notification_enabled
