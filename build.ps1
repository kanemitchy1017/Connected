# Connected - PowerShell Build Script
# より詳細なログ出力とエラーハンドリング

param(
    [switch]$Clean,
    [switch]$Test,
    [switch]$Release
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Connected - Windows Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Python環境チェック
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ エラー: Pythonがインストールされていません" -ForegroundColor Red
    Write-Host "Python 3.9以上をインストールしてください" -ForegroundColor Yellow
    exit 1
}

# 仮想環境の確認
if ($env:VIRTUAL_ENV) {
    Write-Host "✓ 仮想環境: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    Write-Host "⚠ 仮想環境が有効ではありません" -ForegroundColor Yellow
}

# クリーンオプション
if ($Clean) {
    Write-Host "`n🧹 クリーンアップ中..." -ForegroundColor Yellow
    
    $cleanDirs = @("dist", "build", "release", "__pycache__", "*.egg-info")
    foreach ($dir in $cleanDirs) {
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Host "✓ 削除: $dir" -ForegroundColor Green
        }
    }
    
    # Pythonキャッシュファイルも削除
    Get-ChildItem -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
}

# 依存関係のインストール
Write-Host "`n📦 依存関係をインストール中..." -ForegroundColor Blue
try {
    pip install -r requirements.txt --quiet
    pip install pyinstaller --quiet
    Write-Host "✓ 依存関係のインストール完了" -ForegroundColor Green
} catch {
    Write-Host "✗ 依存関係のインストールに失敗" -ForegroundColor Red
    exit 1
}

# テストオプション
if ($Test) {
    Write-Host "`n🧪 テスト実行中..." -ForegroundColor Blue
    try {
        python debug_bluetooth.py
        Write-Host "✓ Bluetoothテスト完了" -ForegroundColor Green
    } catch {
        Write-Host "✗ テストに失敗" -ForegroundColor Red
        exit 1
    }
}

# PyInstallerでexeファイルを作成
Write-Host "`n🔨 Connected.exe を作成中..." -ForegroundColor Blue
Write-Host "これには数分かかる場合があります..." -ForegroundColor Yellow

try {
    pyinstaller Connected.spec --clean --distpath dist --workpath build
    
    if (Test-Path "dist\Connected.exe") {
        $exeSize = (Get-Item "dist\Connected.exe").Length / 1MB
        Write-Host "✓ Connected.exe 作成完了 ($($exeSize.ToString('F1')) MB)" -ForegroundColor Green
    } else {
        throw "exe ファイルが作成されませんでした"
    }
} catch {
    Write-Host "✗ exe作成に失敗: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# リリースパッケージの作成
Write-Host "`n📦 リリースパッケージを作成中..." -ForegroundColor Blue

# リリースディレクトリの準備
if (Test-Path "release") {
    Remove-Item -Recurse -Force "release"
}
New-Item -ItemType Directory -Name "release" | Out-Null

# ファイルのコピー
Copy-Item "dist\Connected.exe" "release\"
Copy-Item "README.md" "release\"
Copy-Item "LICENSE" "release\"

# バージョン情報の取得
$version = "0.2.0"  # 将来的にはgitタグから取得
$buildDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# インストール用READMEの作成
$installGuide = @"
Connected v$version - Windows 11 Bluetooth Battery Monitor
ビルド日時: $buildDate

📋 システム要件:
- Windows 11 (Windows 10でも動作する可能性があります)
- Bluetoothアダプター
- 対応Bluetoothデバイス（ヘッドホン、マウス、キーボードなど）

🚀 インストール方法:
1. Connected.exe をお好みの場所にコピー
   推奨場所: C:\Program Files\Connected\ または C:\Users\%USERNAME%\AppData\Local\Connected\
2. Connected.exe をダブルクリックして起動
3. 初回起動時にWindowsセキュリティの警告が表示される場合は「詳細情報」→「実行」をクリック
4. システムトレイにConnectedのアイコンが表示されます

💡 使用方法:
- システムトレイのアイコンをダブルクリック: メインウィンドウを表示
- システムトレイのアイコンを右クリック: コンテキストメニューを表示
- メインウィンドウ: 接続されているBluetoothデバイスのバッテリー残量を表示
- 自動更新: 1分間隔でバッテリー情報を自動更新
- 低バッテリー通知: バッテリー残量が10%以下になると自動通知

🔧 トラブルシューティング:
- デバイスが検出されない場合:
  * Windowsの設定 → Bluetoothとデバイスでデバイスが接続されているか確認
  * デバイスのBluetooth接続を一度切断して再接続
  * アプリケーションを再起動

- アプリケーションが起動しない場合:
  * Windows Defenderやウイルス対策ソフトによってブロックされていないか確認
  * Connected.exe を右クリック → プロパティ → セキュリティタブで「許可する」にチェック

- バッテリー情報が表示されない場合:
  * 現在はデモ版のため、模擬的なバッテリー情報を表示します
  * 一部のBluetoothデバイスはバッテリー情報を提供しない場合があります

📞 サポート:
- GitHub Issues: https://github.com/YOUR_USERNAME/Connected/issues
- 最新版の確認: https://github.com/YOUR_USERNAME/Connected/releases

🎉 このソフトウェアはMITライセンスの下で公開されています。
"@

Set-Content -Path "release\インストール方法.txt" -Value $installGuide -Encoding UTF8

# リリースオプション
if ($Release) {
    Write-Host "`n📁 ZIPアーカイブを作成中..." -ForegroundColor Blue
    
    $zipName = "Connected-v$version-Windows.zip"
    Compress-Archive -Path "release\*" -DestinationPath $zipName -Force
    
    Write-Host "✓ $zipName を作成しました" -ForegroundColor Green
}

# 完了メッセージ
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🎉 ビルド完了！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n📁 作成されたファイル:" -ForegroundColor White
Write-Host "- release\Connected.exe         : メインアプリケーション" -ForegroundColor Gray
Write-Host "- release\インストール方法.txt    : インストール手順" -ForegroundColor Gray
Write-Host "- release\README.md            : プロジェクト詳細" -ForegroundColor Gray
Write-Host "- release\LICENSE             : ライセンス情報" -ForegroundColor Gray

if ($Release) {
    Write-Host "- Connected-v$version-Windows.zip : 配布用アーカイブ" -ForegroundColor Gray
}

Write-Host "`n🚀 次のステップ:" -ForegroundColor White
Write-Host "1. Connected.exe をテスト: release\Connected.exe をダブルクリック" -ForegroundColor Yellow
Write-Host "2. GitHubに公開: git add . && git commit -m 'Release v$version' && git tag v$version && git push origin main --tags" -ForegroundColor Yellow

if (!$Release) {
    Write-Host "3. ZIPファイル作成: .\build.ps1 -Release" -ForegroundColor Yellow
}

Write-Host "`n⭐ 成功！Connected.exe の準備ができました！" -ForegroundColor Green
