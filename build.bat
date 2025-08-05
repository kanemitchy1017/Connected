@echo off
REM Connected - Build Script for Windows
REM このスクリプトでローカルでexeファイルを作成できます

echo ========================================
echo Connected - Windows Build Script
echo ========================================

REM Python環境チェック
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません
    echo Python 3.9以上をインストールしてください
    pause
    exit /b 1
)

echo Pythonが見つかりました。

REM 依存関係のインストール
echo.
echo 依存関係をインストールしています...
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

REM PyInstallerのインストール
echo.
echo PyInstallerをインストールしています...
pip install pyinstaller
if errorlevel 1 (
    echo エラー: PyInstallerのインストールに失敗しました
    pause
    exit /b 1
)

REM 古いビルドファイルの削除
echo.
echo 古いビルドファイルを削除しています...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM PyInstallerでexeファイルを作成
echo.
echo Connected.exe を作成しています...
echo これには数分かかる場合があります...
pyinstaller Connected.spec
if errorlevel 1 (
    echo エラー: exe作成に失敗しました
    pause
    exit /b 1
)

REM リリースディレクトリの作成
echo.
echo リリースパッケージを作成しています...
if exist "release" rmdir /s /q "release"
mkdir release

copy "dist\Connected.exe" "release\"
copy "README.md" "release\"
copy "LICENSE" "release\"

REM インストール用READMEの作成
echo Connected - Windows 11 Bluetooth Battery Monitor > release\インストール方法.txt
echo. >> release\インストール方法.txt
echo インストール方法: >> release\インストール方法.txt
echo 1. Connected.exe をお好みの場所（例：C:\Program Files\Connected\）にコピー >> release\インストール方法.txt
echo 2. Connected.exe をダブルクリックして起動 >> release\インストール方法.txt
echo 3. 初回起動時にWindowsセキュリティの警告が表示される場合は「詳細情報」→「実行」をクリック >> release\インストール方法.txt
echo 4. システムトレイにアイコンが表示されます >> release\インストール方法.txt
echo. >> release\インストール方法.txt
echo 使用方法: >> release\インストール方法.txt
echo - システムトレイのアイコンをクリックでデバイス一覧表示 >> release\インストール方法.txt
echo - メインウィンドウでBluetoothデバイスのバッテリー残量を確認 >> release\インストール方法.txt
echo - バッテリー残量が低下すると自動通知 >> release\インストール方法.txt
echo. >> release\インストール方法.txt
echo トラブルシューティング: >> release\インストール方法.txt
echo - デバイスが検出されない場合は、Bluetooth設定でデバイスが接続されているか確認してください >> release\インストール方法.txt

REM 完了メッセージ
echo.
echo ========================================
echo ビルド完了！
echo ========================================
echo.
echo 作成されたファイル:
echo - release\Connected.exe        : メインアプリケーション
echo - release\インストール方法.txt  : インストール手順
echo - release\README.md           : プロジェクト詳細
echo - release\LICENSE            : ライセンス情報
echo.
echo Connected.exe をテストするには:
echo   release\Connected.exe をダブルクリック
echo.
echo ZIPファイルを作成するには:
echo   release フォルダを右クリック → 送る → 圧縮（zip形式）フォルダー
echo.

pause
