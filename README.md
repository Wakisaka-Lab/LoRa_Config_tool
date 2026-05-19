# LoRa Config Tool

LoRaモジュール（TLM922S-P01A / ADB922など）のP2P通信パラメータを、シリアル通信経由で一括設定・保存するためのツールです。
Windows環境向けの使いやすいGUI版と、Raspberry PiなどのLinux環境で軽量に動作するCLI版を提供しています。

## 🌟 主な機能

* **クロスプラットフォーム対応**: Windows向けはTkinterによるGUI、Linux向けは対話型のCLIツールとして動作します。
* **一括パラメータ設定**: 周波数、出力(dBm)、拡散係数(SF)、帯域幅(BW)、SyncWordを簡単に設定・モジュールへ書き込めます。
* **電波法に配慮したバリデーション**: 日本の特定小電力無線局で許可されている周波数帯（920.5 MHz ～ 928.1 MHz）から外れた入力に対してはエラーを出し、安全な運用をサポートします。
* **スタンドアロン実行可能（Windows）**: PyInstallerでビルドされた単一の `.exe` ファイルを用意しており、Python環境のないPCでもすぐに使用できます。

## 📁 リポジトリ構成

* `LoRa_Config_tool.py` : Windows向け GUI版スクリプト
* `LoRa_Config_tool_forLinux.py` : Linux向け CLI版スクリプト
* `make_icon.py` : GUI版やexe用のアイコン(`.ico`)生成スクリプト
* `icon.ico` : アプリケーションアイコン
* `dist/LoRa_Config_tool.exe` : ビルド済みのWindows用実行ファイル

## 📦 必要な環境 (ソースコードから実行する場合)

* Python 3.x
* 依存ライブラリ:
  ```bash
  pip install pyserial Pillow
  ```
  ※ `Pillow` はアイコン生成(`make_icon.py`)にのみ使用します。

## 🚀 使い方

### Windows の場合 (GUI)

**方法A: 実行ファイルを使う（推奨）**
1. `dist/` フォルダ内の `LoRa_Config_tool.exe` をダブルクリックして起動します。

**方法B: Pythonスクリプトを実行する**
1. ターミナルで以下を実行します。
   ```bash
   python LoRa_Config_tool.py
   ```
2. 画面左上で認識されているCOMポートとボーレート（通常直結時は `115200`、Arduinoシールド経由は `9600`）を選択します。
3. 各種パラメータを入力し、「モジュールに一括設定を書き込む」をクリックします。

### Linux の場合 (CLI)

1. シリアルポートへのアクセス権限がない場合は、以下のコマンドでユーザーを `dialout` グループに追加し、再起動または再ログインしてください。
   ```bash
   sudo usermod -aG dialout $USER
   ```
2. ターミナルでスクリプトを実行します。
   ```bash
   python3 LoRa_Config_tool_forLinux.py
   ```
3. 画面の指示に従い、使用するポートの番号と各パラメータを対話形式で入力してください。エンターキーのみを押すと推奨されるデフォルト値が適用されます。

## ⚠️ 運用上の注意 (日本の電波法について)

* **周波数**: 本ツールでは 920.5 MHz ～ 928.1 MHz の範囲のみ入力を許可しています。
* **出力 (Power)**: 2 ～ 20 dBm で設定可能ですが、日本国内において 14 dBm 以上で電波を発射すると電波法違反となる恐れがあります。必ず **13 以下** に設定して運用してください。

## 🔧 ビルド方法 (Windows向けexeの再作成)

ソースコードを変更し、新しく `.exe` を作成したい場合は以下のコマンドを実行してください。

```bash
pyinstaller --onefile --noconsole --icon=icon.ico --add-data "icon.ico;." LoRa_Config_tool.py
```
