# Daily Note Poster

テック系の最新ニュースを取得し、Geminiを使って要約記事を自動生成し、note(note.com)へ自動投稿するPythonツールです。

## 主な機能

- **ニュース取得**: 指定したRSSフィード（現在は`ITmedia NEWS`と`Publickey`に設定済）から最新のテック系ニュースを取得します。
- **記事の自動生成**: 取得したニュースを元に、Google Gemini APIを活用して「30代の現役SE（京都出身）」というキャラクター設定に基づいた要約・解説記事を自動生成します。
- **noteへの自動投稿**: 生成した記事をSeleniumを使ってnote.comへ自動的に投稿（または下書き保存）します。
- **自動化（ローカルバッチ）**: macOSの`launchd`を利用して、決まった時間に自動で投稿を走らせるスケジューラー機能が含まれています（現在は停止中）。

## 前提条件

- Python 3.10以上
- macOS環境（`launchd`を利用したスケジューリングを用いる場合）
- Google Chrome（Seleniumで利用）
- [Google Gemini API Key](https://aistudio.google.com/app/apikey)
- note.com のアカウント

## インストールとセットアップ

### 1. リポジトリのクローンと依存関係のインストール

```bash
git clone https://github.com/riverwest-ai/daily-note-poster.git
cd daily-note-poster

# 仮想環境の作成と有効化
python3 -m venv .venv
source .venv/bin/activate

# 依存パッケージのインストール
pip install -r requirements.txt
```

### 2. 環境変数の設定

プロジェクト直下に `.env` ファイルを作成し、GeminiのAPIキーを設定してください。（`.env`はGitで追跡されません）

```env
# .env の内容例
GOOGLE_API_KEY="あなたの_GEMINI_API_キー"
```

### 3. 初期ログイン（Chromeセッションの作成）

noteへの投稿は既存のChromeプロファイルではなく、自動化専用のセッションを使用します。最初に手動でログインを済ませておく必要があります。

```bash
source .venv/bin/activate
python setup_login.py
```

ブラウザが立ち上がるので、**120秒以内**にnote.comにログインしてください。ログイン状態は `chrome_session` フォルダに保存され、以降の自動フェーズで再利用されます。

## 使用方法

### 手動で1回実行する

全体を通して1回だけ記事の生成と投稿を行いたい場合は、以下のスクリプトを実行します。

```bash
./run.sh
```
※このスクリプトは内部で仮想環境を有効化し、`main.py` を実行します。

### 自動投稿のスケジュール設定（macOS）

1日2回（例：朝7:30と夜19:30）自動で実行されるようにスケジュールするには、以下のセットアップスクリプトを実行します。

```bash
./setup_scheduler.sh
```

**スケジュールの停止・再開**
設定されたバッチ処理を（機能はそのままに）一時停止・再開する場合は以下のコマンドを実行します。

```bash
# 停止
launchctl unload ~/Library/LaunchAgents/com.tomac.daily-note-poster.plist

# 再開
launchctl load ~/Library/LaunchAgents/com.tomac.daily-note-poster.plist
```

## プロジェクト構成

- `main.py`: プログラムのエントリポイント。全体の流れを制御します。
- `news_fetcher.py`: RSSフィードからニュースを取得・フィルタリングします。
- `article_generator.py`: 取得したニュースを元にGeminiを用いて記事本文を生成します。
- `note_poster.py`: Seleniumを用いてnote.comに記事を投稿します。
- `setup_login.py`: 初回ログインセッションを確保するためのスクリプト。
- `setup_scheduler.sh`: macOSの`launchd`を利用して自動実行をセットアップするスクリプト。
- `articles/`: 生成されたマークダウン形式の記事が保存されるフォルダです（Git対象外）。

## 注意事項

- Seleniumによる自動操作は、サイト提供側（note.com）のUI変更により動作しなくなる可能性があります。投稿が失敗する場合は、`note_poster.py` のCSS要素指定などを見直す必要があります。
- 記事内で生成される画像に関する機能（`image_fetcher.py`等）は、現在の仕様では無効化/不要とされています。
