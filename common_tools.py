import os
import requests
from class_str_enum import EventIdStrEnum
import json


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


def send_line_masageapi(notification_message: str, line_group_id: str) -> None:
    """
    LINEに通知する
    Args:
        notification_message (str): 送信メッセージ
        line_notify_token (str): 送信宛先LINEトークン。DEMOモードの場合、強制上書き。
    """
    line_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
    if os.getenv("DEMO_MODE") == "1":
        # DEMOモードの場合は強制的にデモ用の宛先へ変更
        line_group_id = os.getenv("LINE_MESSAGE_API_GROUP_ID_DEMO")
    # line_group_id = os.getenv('LINE_MESSAGE_API_GROUP_ID')
    line_api_url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {line_token}',
    }
    data = {
        'to': line_group_id,
        'messages': [
            {
                'type': 'text',
                'text': notification_message,
            },
        ],
    }
    requests.post(line_api_url, headers=headers, data=json.dumps(data))
