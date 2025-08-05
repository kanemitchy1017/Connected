# Connected プロジェクト 開発ガイド

## 開発環境セットアップ

### 1. 必要な環境
- Windows 11 (64bit)
- Python 3.9以上
- Visual Studio Code

### 2. プロジェクトのクローン・セットアップ
```bash
# プロジェクトディレクトリに移動
cd Connected

# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 開発用パッケージのインストール
pip install pytest pytest-asyncio black pylint mypy
```

### 3. 開発用VS Code設定
- Python インタープリターを仮想環境に設定
- 自動フォーマット（Black）を有効化
- Pylint による静的解析を有効化

## プロジェクト構造

```
Connected/
├── src/                     # ソースコード
│   ├── main.py             # メインエントリーポイント
│   ├── bluetooth_manager.py # Bluetooth管理
│   ├── battery_monitor.py   # バッテリー監視
│   ├── notification.py      # 通知機能
│   ├── ui/                 # UI関連
│   │   ├── tray_icon.py    # システムトレイ
│   │   ├── main_window.py  # メインウィンドウ
│   │   └── settings.py     # 設定画面
│   ├── utils/              # ユーティリティ
│   │   ├── config.py       # 設定管理
│   │   └── logger.py       # ログ管理
│   └── resources/          # リソースファイル
│       ├── icons/          # アイコン
│       └── translations/   # 多言語ファイル
├── tests/                  # テストファイル
├── docs/                   # ドキュメント
├── .vscode/               # VS Code設定
├── requirements.txt        # 依存関係
├── setup.py               # インストール設定
└── README.md              # プロジェクト説明
```

## 開発タスク

### アプリケーションの実行
```bash
# 開発環境でアプリを実行
python src/main.py
```

または、VS Codeのデバッグ設定「Python: Connected App」を使用

### テストの実行
```bash
# 全テストを実行
pytest tests/

# 特定のテストファイルを実行
pytest tests/test_bluetooth_manager.py

# カバレッジ付きでテスト実行
pytest tests/ --cov=src
```

### コード品質チェック
```bash
# コードフォーマット
black src/ tests/

# 静的解析
pylint src/

# 型チェック
mypy src/
```

## 実装予定機能

### フェーズ1（基本機能）
- [x] プロジェクト構造の作成
- [x] Bluetooth デバイス検出
- [x] バッテリー情報取得
- [x] システムトレイアイコン
- [x] 基本的な通知機能
- [ ] 設定画面の実装
- [ ] エラーハンドリングの強化

### フェーズ2（拡張機能）
- [ ] ダークモード対応
- [ ] 多言語対応（日本語・英語）
- [ ] バッテリー履歴の記録・表示
- [ ] デバイス固有の設定
- [ ] 自動起動機能

### フェーズ3（最適化）
- [ ] パフォーマンス最適化
- [ ] より正確なBluetoothバッテリー情報取得
- [ ] ユーザビリティ向上
- [ ] インストーラーの作成

## 既知の課題

1. **Bluetoothバッテリー情報取得**
   - 現在は模擬データを使用
   - Windows Battery Reporting API の実装が必要
   - 一部デバイスはバッテリー情報を提供しない

2. **依存関係**
   - PyQt5 の代わりに PyQt6 への移行を検討
   - Windows固有のAPIの活用

3. **パフォーマンス**
   - 定期的なBluetoothスキャンの最適化
   - メモリ使用量の削減

## トラブルシューティング

### Python環境の問題
```bash
# 仮想環境を再作成
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### PyQt5インストールエラー
```bash
# Visual C++ Redistributable が必要な場合があります
# Microsoft公式サイトからダウンロードしてインストール
```

### Bluetoothアクセス権限エラー
- Windows設定でBluetoothアクセス許可を確認
- 管理者権限での実行を試行

## コントリビューション

1. Issue を確認
2. フィーチャーブランチを作成
3. 変更を実装
4. テストを追加・実行
5. プルリクエストを作成

## ライセンス

MIT License - 詳細は LICENSE ファイルを参照
