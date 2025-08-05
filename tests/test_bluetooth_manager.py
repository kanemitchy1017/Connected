"""
Test Bluetooth Manager
"""

import unittest
import asyncio
from unittest.mock import Mock, patch
from src.bluetooth_manager import BluetoothManager, BluetoothDevice


class TestBluetoothManager(unittest.TestCase):

    def setUp(self):
        """テスト前の設定"""
        self.bluetooth_manager = BluetoothManager()

    def test_device_creation(self):
        """デバイス作成テスト"""
        device = BluetoothDevice("Test Device", "00:11:22:33:44:55", "mouse")
        self.assertEqual(device.name, "Test Device")
        self.assertEqual(device.address, "00:11:22:33:44:55")
        self.assertEqual(device.device_type, "mouse")
        self.assertIsNone(device.battery_level)
        self.assertFalse(device.is_connected)

    def test_device_type_determination(self):
        """デバイスタイプ判定テスト"""
        # イヤホン
        self.assertEqual(
            self.bluetooth_manager._determine_device_type("AirPods Pro"), "earphones"
        )

        # ヘッドホン
        self.assertEqual(
            self.bluetooth_manager._determine_device_type("Sony Headphones"),
            "headphones",
        )

        # マウス
        self.assertEqual(
            self.bluetooth_manager._determine_device_type("Bluetooth Mouse"), "mouse"
        )

        # キーボード
        self.assertEqual(
            self.bluetooth_manager._determine_device_type("Magic Keyboard"), "keyboard"
        )

        # 不明
        self.assertEqual(
            self.bluetooth_manager._determine_device_type("Unknown Device"), "unknown"
        )

    async def test_battery_level_retrieval(self):
        """バッテリーレベル取得テスト"""
        device = BluetoothDevice("Test Device", "00:11:22:33:44:55")

        # モック実装では常にランダムな値が返される
        battery_level = await self.bluetooth_manager.get_battery_level(device)
        self.assertIsInstance(battery_level, int)
        if battery_level is not None:
            self.assertTrue(0 <= battery_level <= 100)


if __name__ == "__main__":
    unittest.main()
