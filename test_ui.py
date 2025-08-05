#!/usr/bin/env python3
"""
UI Test Script - UIのテスト用スクリプト
"""

import sys
import os

# src ディレクトリを Python パスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PyQt5.QtWidgets import QApplication
from ui.main_window import ConnectedMainWindow
from bluetooth_manager import BluetoothManager, BluetoothDevice
from battery_monitor import BatteryMonitor


class MockBluetoothManager(BluetoothManager):
    """テスト用のモックBluetoothManager"""

    def __init__(self):
        super().__init__()
        # テスト用のダミーデバイスを作成
        self.mock_devices = {
            "00:11:22:33:44:55": BluetoothDevice(
                "Bluetoothイヤホン", "00:11:22:33:44:55", "earphones"
            ),
            "00:11:22:33:44:56": BluetoothDevice(
                "マウス", "00:11:22:33:44:56", "mouse"
            ),
            "00:11:22:33:44:57": BluetoothDevice(
                "キーボード", "00:11:22:33:44:57", "keyboard"
            ),
        }

        # ダミーのバッテリーレベルを設定
        self.mock_devices["00:11:22:33:44:55"].battery_level = 85
        self.mock_devices["00:11:22:33:44:55"].is_connected = True

        self.mock_devices["00:11:22:33:44:56"].battery_level = 40
        self.mock_devices["00:11:22:33:44:56"].is_connected = True

        self.mock_devices["00:11:22:33:44:57"].battery_level = 12
        self.mock_devices["00:11:22:33:44:57"].is_connected = True

        self.connected_devices = self.mock_devices.copy()

    def get_connected_devices(self):
        """接続されているデバイスを取得"""
        return self.mock_devices.copy()


class MockBatteryMonitor(BatteryMonitor):
    """テスト用のモックBatteryMonitor"""

    def get_battery_status(self):
        """全デバイスのバッテリー状況を取得"""
        status = {}
        connected_devices = self.bluetooth_manager.get_connected_devices()

        for address, device in connected_devices.items():
            status[address] = {
                "name": device.name,
                "device_type": device.device_type,
                "battery_level": device.battery_level,
                "last_updated": device.last_updated,
                "is_low_battery": device.battery_level is not None
                and device.battery_level <= 15,
            }

        return status


def main():
    """テスト用メイン関数"""
    app = QApplication(sys.argv)

    # モックオブジェクトを作成
    mock_bluetooth_manager = MockBluetoothManager()
    mock_battery_monitor = MockBatteryMonitor(mock_bluetooth_manager)

    # メインウィンドウを作成
    window = ConnectedMainWindow(mock_battery_monitor)

    # ウィンドウを表示
    window.show()

    # イベントループを開始
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
