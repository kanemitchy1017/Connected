"""
Battery Monitor - バッテリー監視機能
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from bluetooth_manager import BluetoothManager, BluetoothDevice


class BatteryMonitor:
    """バッテリー監視クラス"""

    def __init__(self, bluetooth_manager: BluetoothManager):
        self.logger = logging.getLogger(__name__)
        self.bluetooth_manager = bluetooth_manager
        self.battery_history: Dict[str, List[tuple]] = (
            {}
        )  # device_address: [(timestamp, battery_level)]
        self.low_battery_threshold = 10  # 初期値10%
        self.notification_sent = set()  # 通知済みデバイスを追跡

    async def update_battery_levels(self):
        """全接続デバイスのバッテリーレベルを更新"""
        try:
            # デバイスをスキャンして更新
            devices = await self.bluetooth_manager.scan_devices()

            updated_count = 0
            for device in devices:
                try:
                    # バッテリーレベルを取得・更新
                    success = await self.bluetooth_manager.update_device_battery_info(
                        device
                    )

                    if success and device.battery_level is not None:
                        # バッテリー履歴に記録
                        self._record_battery_history(
                            device.address, device.battery_level
                        )

                        # 低バッテリー通知をチェック
                        self._check_low_battery_notification(device)

                        updated_count += 1

                except Exception as e:
                    self.logger.error(
                        f"デバイス {device.name} のバッテリー更新エラー: {e}"
                    )

            self.logger.info(f"バッテリー情報を更新したデバイス数: {updated_count}")
            return devices

        except Exception as e:
            self.logger.error(f"バッテリーレベル更新エラー: {e}")
            return []

    def _record_battery_history(self, device_address: str, battery_level: int):
        """バッテリー履歴を記録"""
        try:
            if device_address not in self.battery_history:
                self.battery_history[device_address] = []

            timestamp = datetime.now()
            self.battery_history[device_address].append((timestamp, battery_level))

            # 履歴の上限を設定（最新の100件まで）
            if len(self.battery_history[device_address]) > 100:
                self.battery_history[device_address] = self.battery_history[
                    device_address
                ][-100:]

        except Exception as e:
            self.logger.error(f"バッテリー履歴記録エラー: {e}")

    def _check_low_battery_notification(self, device: BluetoothDevice):
        """低バッテリー通知をチェック"""
        try:
            if (
                device.battery_level is not None
                and device.battery_level <= self.low_battery_threshold
                and device.address not in self.notification_sent
            ):

                self.logger.warning(
                    f"低バッテリー警告: {device.name} - {device.battery_level}%"
                )
                self.notification_sent.add(device.address)

                # 将来的に通知システムを実装
                # notification.send_low_battery_notification(device)

            elif (
                device.battery_level is not None
                and device.battery_level > self.low_battery_threshold + 5
            ):
                # バッテリーが回復した場合、通知状態をリセット
                self.notification_sent.discard(device.address)

        except Exception as e:
            self.logger.error(f"低バッテリー通知チェックエラー: {e}")

    def get_device_battery_history(self, device_address: str) -> List[tuple]:
        """指定されたデバイスのバッテリー履歴を取得"""
        return self.battery_history.get(device_address, [])

    def set_low_battery_threshold(self, threshold: int):
        """低バッテリー閾値を設定"""
        if 0 <= threshold <= 100:
            self.low_battery_threshold = threshold
            self.logger.info(f"低バッテリー閾値を {threshold}% に設定")
            # 通知状態をリセット
            self.notification_sent.clear()
        else:
            self.logger.error(
                f"無効な閾値: {threshold} (0-100の範囲で指定してください)"
            )

    def get_low_battery_devices(self) -> List[BluetoothDevice]:
        """低バッテリーデバイスの一覧を取得"""
        low_battery_devices = []
        try:
            # 現在の連絡先デバイスをチェック（簡易版）
            # 実際の実装では bluetooth_manager から取得
            pass
        except Exception as e:
            self.logger.error(f"低バッテリーデバイス取得エラー: {e}")

        return low_battery_devices

    async def start_monitoring(self, update_interval: int = 60):
        """バッテリー監視を開始"""
        self.logger.info(f"バッテリー監視を開始 (更新間隔: {update_interval}秒)")

        while True:
            try:
                await self.update_battery_levels()
                await asyncio.sleep(update_interval)
            except asyncio.CancelledError:
                self.logger.info("バッテリー監視が停止されました")
                break
            except Exception as e:
                self.logger.error(f"バッテリー監視エラー: {e}")
                await asyncio.sleep(update_interval)  # エラーが発生しても継続
