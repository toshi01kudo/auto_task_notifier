Module common_tools
===================

Functions
---------

`detect_event_type(event: dict) ‑> class_str_enum.EventIdStrEnum`
:   イベント種別を判別するメソッド
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
    Returns:
        event_type (EventIdStrEnum): イベント種別

`send_line_notify(notification_message: str, line_notify_token: str) ‑> None`
:   LINEに通知する
    Args:
        notification_message (str): 送信メッセージ
        line_notify_token (str): 送信宛先LINEトークン。DEMOモードの場合、強制上書き。