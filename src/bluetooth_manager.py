"""
Bluetooth Manager - Bluetoothデバイスの管理
"""

import asyncio
import logging
import subprocess
import json
import re
from typing import List, Dict, Optional
from datetime import datetime


class BluetoothDevice:
    """Bluetoothデバイス情報を格納するクラス"""

    def __init__(self, name: str, address: str, device_type: str = "Unknown"):
        self.name = name
        self.address = address
        self.device_type = device_type
        self.battery_level: Optional[int] = None
        self.is_connected = False
        self.last_updated: Optional[datetime] = None


class BluetoothManager:
    """Bluetoothデバイスの管理クラス"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connected_devices: Dict[str, BluetoothDevice] = {}

    async def scan_devices(self) -> List[BluetoothDevice]:
        """接続されているBluetoothデバイスをスキャン"""
        devices = []
        try:
            # PowerShellを使用してBluetoothデバイスを取得
            devices = self._get_powershell_bluetooth_devices()

            # 接続されているデバイスのみフィルタ
            connected_devices = [device for device in devices if device.is_connected]

            self.logger.info(f"発見されたBluetoothデバイス数: {len(devices)}")
            self.logger.info(
                f"接続されているBluetoothデバイス数: {len(connected_devices)}"
            )

            return connected_devices

        except Exception as e:
            self.logger.error(f"デバイススキャンエラー: {e}")
            return []

    def _get_powershell_bluetooth_devices(self) -> List[BluetoothDevice]:
        """PowerShellを使用してBluetoothデバイスを取得"""
        devices = []
        try:
            # シンプルなBluetoothデバイス一覧取得
            cmd = """
            Get-PnpDevice | Where-Object {
                ($_.Status -eq "OK") -and (
                    $_.FriendlyName -like "*AirPods*" -or
                    $_.FriendlyName -like "*Headphone*" -or
                    $_.FriendlyName -like "*Headset*" -or
                    $_.FriendlyName -like "*Mouse*" -or
                    $_.FriendlyName -like "*Keyboard*" -or
                    $_.FriendlyName -like "*Earphone*" -or
                    $_.FriendlyName -like "*Bluetooth HID*" -or
                    ($_.FriendlyName -like "*Bluetooth*" -and $_.FriendlyName -notlike "*Adapter*" -and $_.FriendlyName -notlike "*Enumerator*" -and $_.FriendlyName -notlike "*汎用*")
                )
            } | Select-Object FriendlyName, Status, InstanceId | ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    device_data = json.loads(result.stdout)
                    if not isinstance(device_data, list):
                        device_data = [device_data]

                    for device in device_data:
                        name = device.get("FriendlyName", "Unknown Device")
                        status = device.get("Status", "Unknown")
                        instance_id = device.get("InstanceId", "")

                        # デバイス名をクリーンアップ
                        clean_name = self._clean_device_name(name)

                        # アドレスを抽出（簡易版）
                        address = self._extract_address_from_instance_id(instance_id)

                        bt_device = BluetoothDevice(
                            name=clean_name,
                            address=address,
                            device_type=self._determine_device_type(clean_name),
                        )
                        bt_device.is_connected = status == "OK"
                        devices.append(bt_device)

                except json.JSONDecodeError as e:
                    self.logger.warning(f"PowerShellからのJSON解析に失敗: {e}")
                    self.logger.debug(f"生の出力: {result.stdout}")

        except Exception as e:
            self.logger.error(f"PowerShell Bluetoothデバイス取得エラー: {e}")

        return devices

    def _clean_device_name(self, name: str) -> str:
        """デバイス名をクリーンアップ"""
        # 不要な文字列を削除
        name = re.sub(
            r" - Find My.*$", "", name
        )  # AirPods Max (Green) - Find My -> AirPods Max (Green)
        name = re.sub(r"^Bluetooth HID デバイス$", "Bluetoothマウス・キーボード", name)
        name = re.sub(
            r"^Bluetooth 低エネルギー GATT 対応 HID デバイス$",
            "Bluetooth HIDデバイス",
            name,
        )
        return name.strip()

    def _extract_address_from_instance_id(self, instance_id: str) -> str:
        """インスタンスIDからMACアドレスを抽出（簡易版）"""
        try:
            # MACアドレスっぽいパターンを探す
            mac_patterns = [
                r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})",  # XX:XX:XX:XX:XX:XX
                r"([0-9A-Fa-f]{12})",  # XXXXXXXXXXXX
                r"DEV_([0-9A-Fa-f]{12})",  # DEV_XXXXXXXXXXXX
                r"([0-9A-Fa-f]{6})([0-9A-Fa-f]{6})",  # XXXXXXYYYYYY
            ]

            for pattern in mac_patterns:
                match = re.search(pattern, instance_id)
                if match:
                    if len(match.groups()) == 2 and len(match.group(0)) >= 12:
                        # 連続する12桁の16進数を見つけた場合
                        mac = match.group(0).replace("-", "").replace(":", "")
                        if len(mac) == 12:
                            return ":".join([mac[i : i + 2] for i in range(0, 12, 2)])
                    elif len(match.group(0)) == 17:  # XX:XX:XX:XX:XX:XX format
                        return match.group(0)

            # 見つからない場合は、インスタンスIDの最後の部分を使用
            parts = instance_id.split("\\")
            if len(parts) > 0:
                return f"ID_{hash(parts[-1]) % 10000:04d}"

        except Exception as e:
            self.logger.debug(f"アドレス抽出エラー: {e}")

        return "Unknown"

    def _determine_device_type(self, name: str) -> str:
        """デバイス名からデバイスタイプを判定"""
        name_lower = name.lower()

        if any(
            keyword in name_lower
            for keyword in ["airpods", "headphone", "headset", "earphone", "buds"]
        ):
            return "ヘッドホン・イヤホン"
        elif any(keyword in name_lower for keyword in ["mouse", "マウス"]):
            return "マウス"
        elif any(keyword in name_lower for keyword in ["keyboard", "キーボード"]):
            return "キーボード"
        elif any(
            keyword in name_lower
            for keyword in ["controller", "gamepad", "コントローラー"]
        ):
            return "ゲームコントローラー"
        elif "hid" in name_lower:
            return "HIDデバイス"
        else:
            return "Bluetoothデバイス"

    async def get_battery_level(self, device: BluetoothDevice) -> Optional[int]:
        """デバイスのバッテリー残量を取得"""
        try:
            # 現在は模擬データを返す（将来的に実装予定）
            if device.name and "airpods" in device.name.lower():
                # AirPodsの場合、模擬的なバッテリーレベル
                import random

                return random.randint(20, 95)
            elif device.device_type in ["マウス", "キーボード"]:
                # マウス・キーボードの場合
                import random

                return random.randint(40, 100)
            else:
                # その他のデバイス
                import random

                return random.randint(10, 85)

        except Exception as e:
            self.logger.error(f"バッテリー残量取得エラー for {device.name}: {e}")
            return None

    async def update_device_battery_info(self, device: BluetoothDevice) -> bool:
        """デバイスのバッテリー情報を更新"""
        try:
            battery_level = await self.get_battery_level(device)
            if battery_level is not None:
                device.battery_level = battery_level
                device.last_updated = datetime.now()
                return True
        except Exception as e:
            self.logger.error(f"バッテリー情報更新エラー for {device.name}: {e}")

        return False
