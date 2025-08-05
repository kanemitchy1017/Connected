#!/usr/bin/env python3
"""
Connected - Bluetooth Device Battery Monitor
メインアプリケーションエントリーポイント
"""

import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from ui.tray_icon import SystemTrayIcon
from ui.main_window import ConnectedMainWindow
from bluetooth_manager import BluetoothManager
from battery_monitor import BatteryMonitor
from utils.config import ConfigManager
from utils.logger import setup_logger


class ConnectedApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.logger = setup_logger()
        self.config = ConfigManager()

        # アプリケーションが終了しないようにする
        self.app.setQuitOnLastWindowClosed(False)

        # コンポーネントの初期化
        self.bluetooth_manager = BluetoothManager()
        self.battery_monitor = BatteryMonitor(self.bluetooth_manager)

        # UIコンポーネント
        self.main_window = ConnectedMainWindow(self.battery_monitor)
        self.tray_icon = SystemTrayIcon(self.battery_monitor, self.config)

        # シグナル接続
        self.setup_signals()

        # タイマーの設定（1分間隔でバッテリー情報を更新）
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_battery_info)
        self.update_timer.start(60000)  # 60秒間隔

        self.logger.info("Connected アプリケーションが開始されました")

    def setup_signals(self):
        """シグナルとスロットを接続"""
        # メインウィンドウのシグナル
        self.main_window.close_requested.connect(self.quit_application)
        self.main_window.refresh_requested.connect(self.update_battery_info)

        # システムトレイのシグナル
        self.tray_icon.show_main_window.connect(self.show_main_window)

    def show_main_window(self):
        """メインウィンドウを表示"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def update_battery_info(self):
        """バッテリー情報を更新"""
        try:
            # 非同期でバッテリー情報を更新
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                devices = loop.run_until_complete(
                    self.battery_monitor.update_battery_levels()
                )

                # UIを更新
                self.main_window.refresh_device_list()
                # システムトレイも更新（後で実装）
                # self.tray_icon.update_icon(devices)

            finally:
                loop.close()

        except Exception as e:
            self.logger.error(f"バッテリー情報の更新に失敗しました: {e}")

    def quit_application(self):
        """アプリケーションを終了"""
        self.logger.info("Connected アプリケーションを終了します")
        self.tray_icon.hide()
        self.app.quit()

    def run(self):
        """アプリケーションを実行"""
        # 初回バッテリー情報取得
        self.update_battery_info()

        # システムトレイアイコンを表示
        self.tray_icon.show()

        # 初回はメインウィンドウも表示
        self.show_main_window()

        # アプリケーションのメインループを開始
        return self.app.exec_()


def main():
    """メイン関数"""
    try:
        app = ConnectedApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"アプリケーションの開始に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
