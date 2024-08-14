Module auto_task_notifier
=========================
This is main function to manage this repogitory.

Functions
---------

`auto_task_notifier_main() ‑> None`
:   スケジュールから自動的にタスクを通知するプログラム
    Args:
        None
    Returns:
        None

`detect_remove_a_tag(description: str) ‑> str`
:   detect & remove HTML a tag.
    Args:
        description (str): the target strings.
    Return:
        str: a pure strings.

`get_events_googlecal(gcal: class_gcalendar.CalendarApi) ‑> list`
:   Google カレンダーからスケジュールを取得する関数
    Args:
        gcal (CalendarApi): Google calendar class
    Returns:
        events (list): 2ヶ月以内の予定されたスケジュールのリスト

`get_next_event(last_event: dict, events: list) ‑> None`
:   次回の同一イベントを取得するメソッド
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
        events (list): Googleカレンダーから取得した直近の予定一覧
    Returns:
        event (dict): 次回のイベント

`get_post_event_list(events: list) ‑> list`
:   数か月先のイベント一覧を取得するメソッド
    Args:
        events (list): Googleカレンダーから取得した直近の予定一覧
    Returns:
        post_events (list): 予定の日付一覧

`goto_each_task(gcal: class_gcalendar.CalendarApi, events: list) ‑> None`
:   具体的なタスクに分岐
    Args:
        gcal (CalendarApi): Google calendar class
        events (list): スケジュールされた予定。タイトルと日付。
    Returns:
        None

`one_week_pre_mgmt(event: dict) ‑> None`
:   イベントの1週間前のリマインド
    * {イベント内容}の1週間前です、と通知
    * 調整さんのURLを送り、参加者の確認を促す
    * （TRPG会なら）各卓のマスターに準備状況をフォローするよう依頼
    * Lineに通知する
    Args:
        event (dict): Google カレンダーのイベント情報
    Returns:
        None

`post_event_mgmt(event: dict, events: list, gcal: class_gcalendar.CalendarApi) ‑> None`
:   ボドゲ会の翌日に行うタスク
    * {イベント内容}お疲れ様でした、と通知
    * 調整さんのURLと収益計算のURLを送り、帳簿を付けるように催促
    * 次回の{イベント内容}の会議室予約を依頼
    * 次回イベント日を自動通知し、調整さんのURLを送る
    * Lineに通知する
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
        events (list): Googleカレンダーから取得した直近の予定一覧
        gcal (CalendarApi): ボドゲ部のGoogleカレンダー操作クラス
    Returns:
        None

`pre_event_mgmt(event: dict) ‑> None`
:   イベントの前日に行うタスク
    * 明日は{イベント内容}です、と通知
    * 集合時間が12:30で間違いないか確認を促す
    * 調整さんのURLを送り、参加者の確認を促す
    * （TRPG会なら）次々回のTRPGの卓内容を考えるようにリマインド
    * Lineに通知する
    Args:
        event (dict): Google カレンダーのイベント情報
    Returns:
        None

`send_error_to_line(line_notify_token: str) ‑> None`
: