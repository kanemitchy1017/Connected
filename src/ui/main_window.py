"""
Main Window - メインウィンドウUI
"""

import sys
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
    QApplication,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPainter, QPixmap
from battery_monitor import BatteryMonitor


class ModernButton(QPushButton):
    """モダンなボタンスタイルのカスタムボタン"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #404040;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
        """
        )


class BatteryIcon(QLabel):
    """バッテリーアイコンウィジェット"""

    def __init__(self, battery_level=None, parent=None):
        super().__init__(parent)
        self.battery_level = battery_level
        self.setFixedSize(40, 20)
        self.update_icon()

    def update_icon(self):
        """バッテリーレベルに応じたアイコンを生成"""
        pixmap = QPixmap(40, 20)
        pixmap.fill(QColor(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # バッテリー外枠 (白色)
        painter.setPen(QColor(255, 255, 255))
        painter.drawRect(2, 4, 32, 12)
        painter.drawRect(34, 7, 4, 6)

        if self.battery_level is not None and self.battery_level >= 0:
            # バッテリーレベルに応じた色と幅
            if self.battery_level <= 15:
                color = QColor(255, 69, 58)  # 赤
            elif self.battery_level <= 40:
                color = QColor(255, 159, 10)  # オレンジ
            else:
                color = QColor(52, 199, 89)  # 緑

            # バッテリー残量を表示
            fill_width = int(28 * self.battery_level / 100)
            painter.fillRect(4, 6, fill_width, 8, color)
        else:
            # 不明状態：グレーでストライプパターン
            painter.fillRect(4, 6, 28, 8, QColor(80, 80, 80))
            # ストライプを追加して不明状態を示す
            painter.setPen(QColor(120, 120, 120))
            for i in range(6, 30, 4):
                painter.drawLine(i, 6, i, 14)

        painter.end()
        self.setPixmap(pixmap)

    def set_battery_level(self, level):
        """バッテリーレベルを設定して更新"""
        self.battery_level = level
        self.update_icon()


class DeviceRow(QFrame):
    """デバイス情報行のウィジェット"""

    def __init__(self, device_name, battery_level, status, parent=None):
        super().__init__(parent)
        self.device_name = device_name
        self.battery_level = battery_level
        self.status = status

        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(
            """
            DeviceRow {
                background-color: transparent;
                border-bottom: 1px solid #404040;
                padding: 8px 0px;
            }
        """
        )

        self.setup_ui()

    def setup_ui(self):
        """UI要素を設定"""
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)

        # デバイス名
        name_label = QLabel(self.device_name)
        name_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: normal;
            }
        """
        )
        name_label.setMinimumWidth(150)
        layout.addWidget(name_label)

        # スペーサー
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # バッテリーアイコン
        battery_icon = BatteryIcon(self.battery_level)
        layout.addWidget(battery_icon)

        # バッテリー残量パーセンテージ
        if self.battery_level is not None and self.battery_level >= 0:
            percentage_label = QLabel(f"{self.battery_level}%")
            percentage_label.setStyleSheet(
                """
                QLabel {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    margin-left: 8px;
                }
            """
            )
            percentage_label.setMinimumWidth(50)
            layout.addWidget(percentage_label)
        else:
            # バッテリー情報が不明の場合
            percentage_label = QLabel("不明")
            percentage_label.setStyleSheet(
                """
                QLabel {
                    color: #808080;
                    font-size: 16px;
                    font-weight: normal;
                    margin-left: 8px;
                }
            """
            )
            percentage_label.setMinimumWidth(50)
            layout.addWidget(percentage_label)

        # スペーサー
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 状態表示
        status_label = QLabel(self.status)
        if (
            self.battery_level is not None
            and self.battery_level >= 0
            and self.battery_level <= 15
        ):
            status_color = "#FF453A"  # 赤
            if self.battery_level <= 10:
                status_text = "低下"
            else:
                status_text = "接続中"
        elif self.battery_level is None or self.battery_level < 0:
            status_color = "#808080"  # グレー
            status_text = "情報取得中"
        else:
            status_color = "#34C759"  # 緑
            status_text = "接続中"

        status_label.setText(status_text)
        status_label.setStyleSheet(
            f"""
            QLabel {{
                color: {status_color};
                font-size: 16px;
                font-weight: normal;
            }}
        """
        )
        status_label.setMinimumWidth(80)
        layout.addWidget(status_label)

        self.setLayout(layout)


class ConnectedMainWindow(QWidget):
    """Connectedアプリケーションのメインウィンドウ"""

    # シグナル定義
    refresh_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, battery_monitor: BatteryMonitor, parent=None):
        super().__init__(parent)
        self.battery_monitor = battery_monitor
        self.device_rows = []

        self.setup_window()
        self.setup_ui()
        self.apply_dark_theme()

        # 自動更新タイマー
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_device_list)
        self.update_timer.start(30000)  # 30秒間隔

    def setup_window(self):
        """ウィンドウの基本設定"""
        self.setWindowTitle("Connected")
        self.setFixedSize(480, 600)
        self.setWindowFlags(Qt.Window)

        # ウィンドウアイコンを設定（後で実装）
        # self.setWindowIcon(QIcon("resources/icons/connected.ico"))

    def setup_ui(self):
        """UI要素を設定"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ヘッダー
        header = self.create_header()
        main_layout.addWidget(header)

        # カラムヘッダー
        column_header = self.create_column_header()
        main_layout.addWidget(column_header)

        # デバイスリストエリア
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)
        self.scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: #2C2C2E;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 4px;
            }
        """
        )

        self.device_list_widget = QWidget()
        self.device_list_layout = QVBoxLayout()
        self.device_list_layout.setContentsMargins(0, 0, 0, 0)
        self.device_list_layout.setSpacing(0)
        self.device_list_widget.setLayout(self.device_list_layout)

        self.scroll_area.setWidget(self.device_list_widget)
        main_layout.addWidget(self.scroll_area)

        # ボタンエリア
        button_area = self.create_button_area()
        main_layout.addWidget(button_area)

        self.setLayout(main_layout)

        # 初期データを読み込み
        self.refresh_device_list()

    def create_header(self):
        """ヘッダーエリアを作成"""
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(
            """
            QFrame {
                background-color: #1C1C1E;
                border-bottom: 1px solid #404040;
            }
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)

        # アプリタイトル
        title_label = QLabel("Connected")
        title_label.setStyleSheet(
            """
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(title_label)

        # スペーサー
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 設定ボタン（歯車アイコン）
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #8E8E93;
                border: none;
                font-size: 20px;
                border-radius: 20px;
            }
            QPushButton:hover {
                background-color: #404040;
                color: white;
            }
        """
        )
        settings_btn.clicked.connect(self.settings_requested.emit)
        layout.addWidget(settings_btn)

        header.setLayout(layout)
        return header

    def create_column_header(self):
        """カラムヘッダーを作成"""
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet(
            """
            QFrame {
                background-color: #1C1C1E;
                border-bottom: 1px solid #404040;
            }
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 0, 16, 0)

        # カラムタイトル
        device_label = QLabel("デバイス名")
        device_label.setStyleSheet(
            """
            QLabel {
                color: #8E8E93;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        device_label.setMinimumWidth(150)
        layout.addWidget(device_label)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        battery_label = QLabel("バッテリー残量")
        battery_label.setStyleSheet(
            """
            QLabel {
                color: #8E8E93;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        layout.addWidget(battery_label)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        status_label = QLabel("状態")
        status_label.setStyleSheet(
            """
            QLabel {
                color: #8E8E93;
                font-size: 14px;
                font-weight: bold;
            }
        """
        )
        status_label.setMinimumWidth(80)
        layout.addWidget(status_label)

        header.setLayout(layout)
        return header

    def create_button_area(self):
        """ボタンエリアを作成"""
        button_area = QFrame()
        button_area.setFixedHeight(120)
        button_area.setStyleSheet(
            """
            QFrame {
                background-color: #1C1C1E;
                border-top: 1px solid #404040;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 再読み込みボタン
        refresh_btn = ModernButton("再読み込み")
        refresh_btn.clicked.connect(self.refresh_device_list)
        layout.addWidget(refresh_btn)

        # 下部ボタン行
        bottom_layout = QHBoxLayout()

        # 通知設定ボタン
        settings_btn = ModernButton("通知設定")
        settings_btn.clicked.connect(self.settings_requested.emit)
        bottom_layout.addWidget(settings_btn)

        # 終了ボタン
        quit_btn = ModernButton("終了")
        quit_btn.clicked.connect(self.close_requested.emit)
        bottom_layout.addWidget(quit_btn)

        layout.addLayout(bottom_layout)
        button_area.setLayout(layout)
        return button_area

    def apply_dark_theme(self):
        """ダークテーマを適用"""
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2C2C2E;
                color: white;
                font-family: "Segoe UI", "Yu Gothic UI", "Meiryo UI";
            }
        """
        )

    def refresh_device_list(self):
        """デバイスリストを更新"""
        # 既存のデバイス行をクリア
        self.clear_device_list()

        # 非同期でデバイス情報を取得
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                devices = loop.run_until_complete(
                    self.battery_monitor.update_battery_levels()
                )
            finally:
                loop.close()
        except Exception as e:
            print(f"デバイス情報取得エラー: {e}")
            devices = []

        if not devices:
            # デバイスが見つからない場合
            no_device_label = QLabel("接続されているBluetoothデバイスがありません")
            no_device_label.setStyleSheet(
                """
                QLabel {
                    color: #8E8E93;
                    font-size: 16px;
                    padding: 40px;
                    text-align: center;
                }
            """
            )
            self.device_list_layout.addWidget(no_device_label)
        else:
            # デバイス情報を表示
            for device in devices:
                battery_level = (
                    device.battery_level if device.battery_level is not None else -1
                )
                status_text = "接続中" if device.is_connected else "切断"

                device_row = DeviceRow(device.name, battery_level, status_text)
                self.device_list_layout.addWidget(device_row)
                self.device_rows.append(device_row)

        # 下部にスペーサーを追加
        self.device_list_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def clear_device_list(self):
        """デバイスリストをクリア"""
        while self.device_list_layout.count():
            child = self.device_list_layout.takeAt(0)
            if child and child.widget():
                widget = child.widget()
                if widget:
                    widget.deleteLater()
        self.device_rows.clear()


# テスト用のメイン関数
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ダミーのバッテリーモニターを作成
    from bluetooth_manager import BluetoothManager

    bluetooth_manager = BluetoothManager()
    battery_monitor = BatteryMonitor(bluetooth_manager)

    # メインウィンドウを表示
    window = ConnectedMainWindow(battery_monitor)
    window.show()

    sys.exit(app.exec_())
