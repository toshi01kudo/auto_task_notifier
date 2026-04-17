Module auto_task_notifier
=========================
This is main function to manage this repogitory.

Functions
---------

`auto_task_notifier_main() ‑> None`
:   スケジュールから自動的にタスクを通知するプログラム

`detect_remove_a_tag(description: str) ‑> str`
:   detect & remove HTML a tag.
    Args:
        description (str): the target strings.
    Return:
        str: a pure strings.

`send_error_to_line(line_group_id: str) ‑> None`
:   エラー発生時にLINEグループへ通知する

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