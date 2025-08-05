# Connected - Bluetooth Device Battery Monitor

<div align="center">

![Connected Logo](https://img.shields.io/badge/Connected-v0.2.0-blue?style=for-the-badge&logo=bluetooth)
[![Windows 11](https://img.shields.io/badge/Windows-11-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

**Windows 11用Bluetoothデバイスのバッテリー残量監視アプリケーション**

[📥 最新版をダウンロード](https://github.com/YOUR_USERNAME/Connected/releases/latest) | [📖 使用方法](#使用方法) | [🐛 バグ報告](https://github.com/YOUR_USERNAME/Connected/issues)

</div>

---

## 🚀 クイックスタート

1. **ダウンロード**: [最新のリリース](https://github.com/YOUR_USERNAME/Connected/releases/latest)から `Connected-vX.X.X-Windows.zip` をダウンロード
2. **解凍**: ZIPファイルを解凍し、`Connected.exe` を任意の場所にコピー
3. **起動**: `Connected.exe` をダブルクリックして起動
4. **確認**: システムトレイにConnectedアイコンが表示されたら完了！

## プロジェクト概要

ConnectedはWindows 11でBluetooth接続しているデバイス（イヤホン、ヘッドホン、マウス、キーボード）のバッテリー残量を視覚的に確認できるタスクトレイ常駐型アプリケーションです。

## 機能

### 🔋 バッテリー監視
- Bluetoothデバイスのバッテリー残量をリアルタイム表示
- バッテリーアイコンと％表示による視覚的な確認
- 複数デバイス同時監視（最大5台）

### 🎨 モダンなUI
- **ダークテーマ対応**: 目に優しいダークインターフェース
- **直感的なデザイン**: デバイス情報が一目で分かるレイアウト
- **バッテリーアイコン**: 残量に応じて色が変化（緑→オレンジ→赤）
- **ステータス表示**: 接続状態とバッテリー警告を色分け表示

### 🔔 通知機能
- バッテリー低下時の自動通知
- 設定可能な通知閾値（初期値：10%）
- システムトレイからの簡易情報表示

### ⚙️ システム統合
- **タスクトレイ常駐**: リソース消費を最小限に抑制
- **自動更新**: 1分間隔でバッテリー情報を自動取得
- **手動更新**: ワンクリックで即座に情報を更新

## スクリーンショット

メインUIは以下のような機能を提供します：

```
┌─────────────────────────────────────┐
│ Connected                        ⚙  │
├─────────────────────────────────────┤
│ デバイス名    バッテリー残量    状態  │
├─────────────────────────────────────┤
│ Bluetoothイヤホン  🔋 85%      接続中│
│ マウス            🔋 40%      接続中│
│ キーボード         🔋 12%      低下 │
├─────────────────────────────────────┤
│              再読み込み              │
│                                     │
│   通知設定           終了           │
└─────────────────────────────────────┘
```

## 技術スタック

- **言語**: Python 3.9+
- **GUI フレームワーク**: PyQt5
- **Bluetooth通信**: bleak + Windows API
- **通知システム**: plyer + Windows Toast通知
- **設定管理**: JSON設定ファイル

## プロジェクト構造

```
Connected/
├── src/                    # メインソースコード
│   ├── main.py            # アプリケーションエントリーポイント
│   ├── bluetooth_manager.py # Bluetooth デバイス管理
│   ├── battery_monitor.py  # バッテリー監視機能
│   ├── notification.py     # 通知システム
│   ├── ui/                # ユーザーインターフェース
│   │   ├── main_window.py # メインウィンドウ（新デザイン）
│   │   └── tray_icon.py   # システムトレイアイコン
│   └── utils/             # ユーティリティ
│       ├── config.py      # 設定管理
│       └── logger.py      # ログ管理
├── tests/                 # テストファイル
├── docs/                  # ドキュメント
├── .vscode/              # VS Code設定
├── test_ui.py            # UI開発テスト用スクリプト
└── 要件定義書.md         # プロジェクト要件定義
```

## 開発環境

### 必要な依存関係

```
PyQt5>=5.15.0
bleak>=0.19.0
pywin32>=227
plyer>=2.1
configparser>=5.3.0
```

### セットアップ手順

1. **リポジトリのクローン**
```bash
cd Connected
```

2. **Python環境の確認**
```bash
python --version  # Python 3.9+ が必要
```

3. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

### 実行方法

#### 🎯 メインアプリケーション
```bash
python src/main.py
```

#### 🧪 UI開発テスト
```bash
python test_ui.py
```

#### ⚡ VS Codeデバッグ
- F5キーを押すか、「Python: Connected App」設定を使用

### テストの実行
```bash
pytest tests/
```

## 使用方法

### 初回起動
1. アプリケーションを起動すると、システムトレイにConnectedアイコンが表示されます
2. 同時にメインウィンドウが開き、接続されているBluetoothデバイスが表示されます
3. 自動的にバッテリー情報の取得が開始されます

### 操作方法

#### システムトレイ
- **左クリック**: 簡易バッテリー情報をポップアップ表示
- **ダブルクリック**: メインウィンドウを表示
- **右クリック**: コンテキストメニューを表示

#### メインウィンドウ
- **再読み込み**: バッテリー情報を手動更新
- **通知設定**: 通知の設定を変更（今後実装予定）
- **終了**: アプリケーションを完全終了

### バッテリー表示について

#### アイコンの色分け
- 🟢 **緑色** (41%以上): 十分な残量
- 🟠 **オレンジ色** (16-40%): 注意が必要
- 🔴 **赤色** (15%以下): 充電が必要

#### 状態表示
- **接続中**: デバイスが正常に接続されている
- **低下**: バッテリー残量が設定閾値以下

## 設定

### 基本設定
- **低バッテリー閾値**: 通知を送る残量レベル（初期値：10%）
- **更新間隔**: バッテリー情報の更新間隔（初期値：1分）
- **通知有効/無効**: 通知機能のオン/オフ

設定ファイルは `%APPDATA%\Connected\config.json` に保存されます。

## 開発情報

### 現在の実装状況
- ✅ 基本的なBluetoothデバイス検出
- ✅ モダンなダークテーマUI
- ✅ システムトレイ統合
- ✅ 設定管理システム
- ✅ ログシステム
- ⚠️ バッテリー情報取得（模擬データ使用中）
- ⏳ 実際のBluetoothバッテリーAPI実装（作業中）

### 既知の制限事項
1. **バッテリー情報取得**: 現在は開発用の模擬データを使用
2. **デバイス互換性**: 一部のBluetoothデバイスはバッテリー情報を提供しない場合があります
3. **Windows版のみ**: 現在はWindows 11専用（将来的に他OSサポート予定）

### 今後の開発予定
- [ ] 実際のWindows Bluetooth Battery APIの実装
- [ ] 設定画面UI
- [ ] 多言語対応（日本語・英語）
- [ ] バッテリー履歴グラフ
- [ ] 自動起動設定
- [ ] インストーラー作成

## トラブルシューティング

### よくある問題

**Q: `ModuleNotFoundError: No module named 'PyQt5'`**
A: 依存関係が正しくインストールされていません。`pip install -r requirements.txt` を実行してください。

**Q: バッテリー情報が表示されない**
A: 現在は開発版のため模擬データを使用しています。実際のデバイス情報表示は今後実装予定です。

**Q: アプリケーションが起動しない**
A: Windows 11のBluetooth機能が有効になっているか確認してください。

### ログファイル
問題が発生した場合は、以下の場所のログファイルを確認してください：
```
%APPDATA%\Connected\logs\connected.log
```

## コントリビューション

1. Issueを確認または作成
2. フィーチャーブランチを作成: `git checkout -b feature/new-feature`
3. 変更をコミット: `git commit -am 'Add new feature'`
4. ブランチにプッシュ: `git push origin feature/new-feature`
5. プルリクエストを作成

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

---

**Connected v0.2**  
© 2025 Connected Project

Windows 11でBluetoothデバイスのバッテリー管理をより簡単に、より美しく。
