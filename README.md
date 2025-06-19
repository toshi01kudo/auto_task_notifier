# auto_task_notifier

タスク自動通知用のリポジトリです。  
Google カレンダーから予定を取得し、調整さんを作成して、LINE へ自動で通知します。

## 主な機能

- Google カレンダーから予定情報を取得
- 調整さんのイベント自動生成
- 生成したイベント情報をLINEへ通知
- テンプレートによる通知コメントのカスタマイズ

## セットアップ

### 1. 必要なもの

- Python 3.11 以上
- Google カレンダーAPI利用のための認証情報
- LINE Notifyのアクセストークン

### 2. リポジトリのクローン

```sh
git clone https://github.com/toshi01kudo/auto_task_notifier.git
cd auto_task_notifier
```

### 3. 依存ライブラリのインストール

```sh
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example` を参考に `.env` を作成し、各種APIキーやトークンを設定してください。

```
GOOGLE_API_KEY=your_google_api_key
LINE_NOTIFY_TOKEN=your_line_notify_token
...
```

## 使い方

```sh
python auto_task_notifier.py
```

- 日程調整イベントの自動作成・通知が実行されます。
- 詳細な実行方法やパラメータについては各Pythonファイル内のコメントも参照してください。

## ファイル構成

- `auto_task_notifier.py` ... メインスクリプト
- `class_gcalendar.py` ... Googleカレンダー連携用クラス
- `make_choseisan.py` ... 調整さんイベント生成用モジュール
- `common_tools.py` ... 共通ユーティリティ
- `template_choseisan_bdg_comment.txt` など ... 通知用テンプレート
- `requirements.txt` ... 必要なPythonパッケージ
- `.env.example` ... 環境変数サンプル

## Google/LINE連携の設定

- GoogleカレンダーAPIの認証情報取得や、LINE Notifyのトークン発行方法は公式ドキュメント等をご参照ください。
  - [Google Calendar API](https://developers.google.com/calendar)
  - [LINE Notify](https://notify-bot.line.me/ja/)

## ライセンス

このリポジトリのライセンスは `MIT` です。

---

> 質問・要望があれば [Issues](https://github.com/toshi01kudo/auto_task_notifier/issues) までどうぞ。
