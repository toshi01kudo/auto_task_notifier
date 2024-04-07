import os
import requests
from class_str_enum import EventIdStrEnum


def detect_event_type(event: dict) -> EventIdStrEnum:
    """
    イベント種別を判別するメソッド
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
    Returns:
        event_type (EventIdStrEnum): イベント種別
    """
    if "ボドゲ" in event["summary"]:
        event_type = EventIdStrEnum.BOARDGAME
    elif "TRPG" in event["summary"]:
        event_type = EventIdStrEnum.TRPG
    else:
        event_type = EventIdStrEnum.OTHERS
    return event_type


def send_line_notify(notification_message: str, line_notify_token: str) -> None:
    """
    LINEに通知する
    Args:
        notification_message (str): 送信メッセージ
        line_notify_token (str): 送信宛先LINEトークン。DEMOモードの場合、強制上書き。
    """
    if os.getenv("DEMO_MODE") == "1":
        # DEMOモードの場合は強制的にデモ用の宛先へ変更
        line_notify_token = os.getenv("LINE_DEMO_TOKEN_KEY")
    line_notify_api = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {line_notify_token}"}
    data = {"message": notification_message}
    requests.post(line_notify_api, headers=headers, data=data)
