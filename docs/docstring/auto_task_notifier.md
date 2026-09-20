Module auto_task_notifier
=========================
This is main function to manage this repogitory.

Functions
---------

`auto_task_notifier_main(today: datetime.date | None = None) ‑> None`
:   スケジュールから自動的にタスクを通知するプログラム
    Args:
        today (datetime.date | None): 毎月1日の全体向け予定周知の判定に使う日付。None なら実行日。

`build_schedule_announcement(events: list[auto_task_notifier.Event], today: datetime.date, calendar_url: str | None) ‑> str`
:   全体向けの今後の予定一覧メッセージを組み立てる

`create_choseisan_by_date_main(target_date_str: str) ‑> None`
:   指定日のイベントに対して調整さんを作成し、Google カレンダーに URL を登録する

`create_choseisan_for_event(gcal: class_gcalendar.CalendarApi, event: auto_task_notifier.Event) ‑> str`
:   指定イベントの調整さんを作成し、Google カレンダーに URL を登録する

`detect_remove_a_tag(description: str) ‑> str`
:   detect & remove HTML a tag.
    Args:
        description (str): the target strings.
    Return:
        str: a pure strings.

`fetch_events_for_announcement(gcal: class_gcalendar.CalendarApi, today: datetime.date) ‑> list[auto_task_notifier.Event]`
:   全体向けの予定一覧に載せる範囲（today から翌々月末まで）を含む予定を取得する

`notify_schedule_main(today: datetime.date | None = None) ‑> None`
:   全体向け LINE グループへ今後の予定一覧を手動で送信する

`notify_schedule_to_users(events: list[auto_task_notifier.Event], today: datetime.date) ‑> None`
:   全体向け LINE グループへ今後の予定一覧を送信する

`send_error_to_line(line_group_id: str) ‑> None`
:   

Classes
-------

`Event(raw: dict)`
:   Google Calendar イベントのラッパー

    ### Instance variables

    `clean_description: str`
    :   HTMLのaタグを除去した説明文を返す

    `date: datetime.date`
    :

    `description: str | None`
    :

    `event_type: class_str_enum.EventIdStrEnum`
    :

    `summary: str`
    :

    ### Methods

    `days_from_today(self) ‑> int`
    :   今日からの日数差を返す（未来なら正、過去なら負）

    `is_trpg(self) ‑> bool`
    :

`EventNotifier(gcal: class_gcalendar.CalendarApi, group_id: str)`
:   イベントに応じたLINE通知を管理する

    ### Methods

    `notify(self, message: str) ‑> None`
    :

    `on_one_week_before(self, event: auto_task_notifier.Event) ‑> None`
    :   イベント1週間前のリマインド

    `on_post_event(self, event: auto_task_notifier.Event, all_events: list[auto_task_notifier.Event]) ‑> None`
    :   イベント翌日のタスク

    `on_pre_event(self, event: auto_task_notifier.Event) ‑> None`
    :   イベント前日のタスク

    `process_events(self, events: list[auto_task_notifier.Event]) ‑> None`
    :   全イベントを走査し、該当するタスクを実行する