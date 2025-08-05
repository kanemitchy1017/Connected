"""
System Tray Icon - システムトレイアイコン
"""

import sys
import logging
from PyQt5.QtWidgets import (
    QSystemTrayIcon,
    QMenu,
    QAction,
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QHBoxLayout,
    QMessageBox,
)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QColor
from battery_monitor import BatteryMonitor
from utils.config import ConfigManager


class SystemTrayIcon(QSystemTrayIcon):
    """システムトレイアイコンクラス"""

    # シグナル定義
    show_main_window = pyqtSignal()
    quit_application = pyqtSignal()

    def __init__(
        self,
        battery_monitor: BatteryMonitor,
        config_manager: ConfigManager,
        parent=None,
    ):
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)
        self.battery_monitor = battery_monitor
        self.config_manager = config_manager

        # アイコンとメニューの初期化
        self.setup_icon()
        self.setup_menu()

        # トレイアイコンのクリックイベント
        self.activated.connect(self.on_tray_icon_activated)

        # バッテリー情報表示ウィンドウ
        self.battery_window = None

        self.logger.info("システムトレイアイコンが初期化されました")

    def setup_icon(self):
        """トレイアイコンを設定"""
        # 初期アイコンを設定（実際のアイコンファイルまたは生成されたアイコン）
        icon = self.create_battery_icon(None)
        self.setIcon(icon)
        self.setToolTip("Connected - Bluetoothデバイス バッテリー監視")

    def setup_menu(self):
        """コンテキストメニューを設定"""
        menu = QMenu()

        # メインウィンドウ表示
        self.main_window_action = QAction("メインウィンドウを表示", self)
        self.main_window_action.triggered.connect(self.show_main_window.emit)
        menu.addAction(self.main_window_action)

        # バッテリー状況表示
        self.battery_action = QAction("バッテリー状況を表示", self)
        self.battery_action.triggered.connect(self.show_battery_status)
        menu.addAction(self.battery_action)

        menu.addSeparator()

        # 設定
        settings_action = QAction("設定", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)

        # 更新
        refresh_action = QAction("手動更新", self)
        refresh_action.triggered.connect(self.manual_refresh)
        menu.addAction(refresh_action)

        menu.addSeparator()

        # バージョン情報
        about_action = QAction("バージョン情報", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        # 終了
        quit_action = QAction("終了", self)
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def create_battery_icon(self, battery_level=None):
        """バッテリーレベルに応じたアイコンを生成"""
        # 16x16のアイコンを生成
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(0, 0, 0, 0))  # 透明

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        if battery_level is None:
            # 不明状態：グレーのアイコン
            painter.setBrush(QColor(128, 128, 128))
            painter.drawRect(2, 4, 10, 8)
            painter.drawRect(12, 6, 2, 4)
        else:
            # バッテリーレベルに応じた色
            if battery_level <= 10:
                color = QColor(255, 0, 0)  # 赤
            elif battery_level <= 25:
                color = QColor(255, 255, 0)  # 黄
            else:
                color = QColor(0, 255, 0)  # 緑

            # バッテリー外枠
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(2, 4, 10, 8)
            painter.drawRect(12, 6, 2, 4)

            # バッテリー残量
            painter.setBrush(color)
            fill_width = int(8 * battery_level / 100)
            painter.drawRect(3, 5, fill_width, 6)

        painter.end()
        return QIcon(pixmap)

    def update_icon(self, devices_status):
        """デバイス状況に応じてアイコンを更新"""
        if not devices_status:
            # デバイスが接続されていない
            icon = self.create_battery_icon(None)
            tooltip = "Connected - 接続デバイスなし"
        else:
            # 最も低いバッテリーレベルを取得
            min_battery = min(
                device["battery_level"]
                for device in devices_status.values()
                if device["battery_level"] is not None
            )

            icon = self.create_battery_icon(min_battery)

            # ツールチップにデバイス情報を表示
            tooltip_lines = ["Connected - Bluetoothデバイス"]
            for device in devices_status.values():
                if device["battery_level"] is not None:
                    tooltip_lines.append(
                        f"{device['name']}: {device['battery_level']}%"
                    )
                else:
                    tooltip_lines.append(f"{device['name']}: 不明")

            tooltip = "\n".join(tooltip_lines)

        self.setIcon(icon)
        self.setToolTip(tooltip)

    def on_tray_icon_activated(self, reason):
        """トレイアイコンがクリックされた時の処理"""
        if reason == 2:  # QSystemTrayIcon.DoubleClick
            self.show_main_window.emit()
        elif reason == 3:  # QSystemTrayIcon.Trigger
            # 左クリック：簡易情報表示
            self.show_quick_info()

    def show_quick_info(self):
        """簡易情報をバルーンチップで表示"""
        devices_status = self.battery_monitor.get_battery_status()

        if not devices_status:
            self.showMessage("Connected", "Bluetoothデバイスが接続されていません")
            return

        # バッテリー情報のサマリーを作成
        info_lines = []
        for device in devices_status.values():
            if device["battery_level"] is not None:
                status = "⚠️" if device["is_low_battery"] else "🔋"
                info_lines.append(
                    f"{status} {device['name']}: {device['battery_level']}%"
                )
            else:
                info_lines.append(f"❓ {device['name']}: 不明")

        message = "\n".join(info_lines)
        self.showMessage("バッテリー状況", message)

    def show_battery_status(self):
        """詳細バッテリー状況ウィンドウを表示"""
        if self.battery_window is None:
            self.battery_window = BatteryStatusWindow(self.battery_monitor)

        self.battery_window.update_status()
        self.battery_window.show()
        self.battery_window.raise_()
        self.battery_window.activateWindow()

    def show_settings(self):
        """設定ウィンドウを表示"""
        # 設定ウィンドウの実装（今後追加）
        QMessageBox.information(None, "設定", "設定機能は開発中です")

    def manual_refresh(self):
        """手動でバッテリー情報を更新"""
        import asyncio

        # 非同期でバッテリー情報を更新
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.battery_monitor.update_battery_levels())
            self.showMessage("Connected", "バッテリー情報を更新しました")
        except Exception as e:
            self.logger.error(f"手動更新エラー: {e}")
            self.showMessage("Connected", "更新に失敗しました")
        finally:
            loop.close()

    def show_about(self):
        """バージョン情報を表示"""
        QMessageBox.about(
            None,
            "Connected について",
            """Connected v0.2
            
Windows 11 Bluetoothデバイス バッテリー監視アプリ

© 2025 Connected Project
            """,
        )

    def quit_app(self):
        """アプリケーションを終了"""
        QApplication.quit()


class BatteryStatusWindow(QWidget):
    """バッテリー状況表示ウィンドウ"""

    def __init__(self, battery_monitor: BatteryMonitor):
        super().__init__()
        self.battery_monitor = battery_monitor
        self.setWindowTitle("Connected - バッテリー状況")
        self.setFixedSize(400, 300)
        self.setup_ui()

    def setup_ui(self):
        """UIを設定"""
        layout = QVBoxLayout()

        # タイトル
        title_label = QLabel("Bluetoothデバイス バッテリー状況")
        title_label.setFont(QFont("", 12, QFont.Bold))
        title_label.setStyleSheet("text-align: center;")
        layout.addWidget(title_label)

        # デバイスリスト表示エリア
        self.device_layout = QVBoxLayout()
        layout.addLayout(self.device_layout)

        self.setLayout(layout)

    def update_status(self):
        """バッテリー状況を更新"""
        # 既存のウィジェットをクリア
        self.clear_device_widgets()

        devices_status = self.battery_monitor.get_battery_status()

        if not devices_status:
            no_device_label = QLabel("接続されているBluetoothデバイスがありません")
            no_device_label.setStyleSheet("text-align: center;")
            self.device_layout.addWidget(no_device_label)
            return

        # 各デバイスの情報を表示
        for device in devices_status.values():
            device_widget = self.create_device_widget(device)
            self.device_layout.addWidget(device_widget)

    def create_device_widget(self, device_info):
        """デバイス情報ウィジェットを作成"""
        widget = QWidget()
        layout = QVBoxLayout()

        # デバイス名
        name_label = QLabel(device_info["name"])
        name_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(name_label)

        # バッテリー情報
        battery_layout = QHBoxLayout()

        if device_info["battery_level"] is not None:
            # プログレスバー
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(device_info["battery_level"])

            # 色を設定
            if device_info["is_low_battery"]:
                progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: red; }"
                )
            elif device_info["battery_level"] <= 25:
                progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: orange; }"
                )
            else:
                progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: green; }"
                )

            battery_layout.addWidget(progress_bar)

            # パーセンテージ表示
            percentage_label = QLabel(f"{device_info['battery_level']}%")
            battery_layout.addWidget(percentage_label)
        else:
            # バッテリー情報不明
            unknown_label = QLabel("バッテリー情報取得不可")
            battery_layout.addWidget(unknown_label)

        layout.addLayout(battery_layout)
        widget.setLayout(layout)

        return widget

    def clear_device_widgets(self):
        """デバイスウィジェットをクリア"""
        while self.device_layout.count():
            child = self.device_layout.takeAt(0)
            if child and child.widget():
                child.widget().deleteLater()
