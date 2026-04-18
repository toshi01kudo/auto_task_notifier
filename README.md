# auto_task_notifier

タスク自動通知用のリポジトリです。  
Google カレンダーから予定を取得し、調整さんを作成して、LINE へ自動で通知します。

## 主な機能

- Google カレンダーから予定情報を取得
- 調整さんのイベント自動生成
- 生成したイベント情報を LINE Messaging API で通知
- テンプレートによる通知コメントのカスタマイズ
- 指定日のイベントに対する調整さんの手動作成

## セットアップ

### 1. 必要なもの

- Python 3.11 以上
- Google カレンダーAPI利用のための認証情報
- LINE Messaging API のチャネルアクセストークン

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
...
CALENDAR_ID=your_google_calendar_id
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
...
```

## 使い方

### 自動通知（通常実行）

```sh
python auto_task_notifier.py
```

Google カレンダーの予定を走査し、イベントの1週間前・前日・翌日に応じた LINE 通知を自動で送信します。

### 指定日の調整さん作成

```sh
python auto_task_notifier.py --create-choseisan DATE
```

日付は以下の形式に対応しています。

- `YYYY-MM-DD` (例: `2026-04-19`)
- `YYYYMMDD` (例: `20260419`)
- `YYYY/MM/DD` (例: `2026/04/19`)
- `YYYY.MM.DD` (例: `2026.04.19`)

指定日に登録されている Google カレンダーのイベントに対して調整さんを作成し、URL をカレンダーの説明欄に登録します。LINE 通知は行いません。既に説明が登録されているイベントはスキップされます。

## ファイル構成

- `auto_task_notifier.py` ... メインスクリプト
- `class_gcalendar.py` ... Googleカレンダー連携用クラス
- `make_choseisan.py` ... 調整さんイベント生成用モジュール
- `common_tools.py` ... 共通ユーティリティ
- `template_choseisan_bdg_comment.txt` など ... 通知用テンプレート
- `requirements.txt` ... 必要なPythonパッケージ
- `.env.example` ... 環境変数サンプル

## Google/LINE連携の設定

- GoogleカレンダーAPIの認証情報取得や、LINE Messaging API のチャネルアクセストークン発行方法は公式ドキュメント等をご参照ください。
  - [Google Calendar API](https://developers.google.com/calendar)
  - [LINE Messaging API](https://developers.line.biz/ja/docs/messaging-api/)

## ライセンス

このリポジトリのライセンスは `MIT` です。

---

> 質問・要望があれば [Issues](https://github.com/toshi01kudo/auto_task_notifier/issues) までどうぞ。
