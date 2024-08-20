"""
This is main function to manage this repogitory.
"""

import logging
from dotenv import load_dotenv
import datetime
import os
import re
import locale
from class_gcalendar import CalendarApi, EventNotFoundException
from make_choseisan import make_choseisan
from common_tools import detect_event_type, send_line_notify


# Parameters ------------------
JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
# localeモジュールで曜日を日本語表示にする
try:
    if os.name == "nt":  # Windows
        locale.setlocale(locale.LC_TIME, ".932")
    else:
        locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
except ImportError as e:
    logging.error(f"Error: {e}")
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
except locale.Error as e:
    logging.error(f"Error: {e}")
    locale.setlocale(locale.LC_TIME, "en_US.UTF-8")


# Main ---
def auto_task_notifier_main() -> None:
    """
    スケジュールから自動的にタスクを通知するプログラム
    Args:
        None
    Returns:
        None
    """
    # Logging
    logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")
    logging.info("#=== Start program ===#")

    # load parameters
    load_dotenv()

    # スケジュールを取得
    try:
        gcal = CalendarApi()
        events = get_events_googlecal(gcal)
    except Exception as e:
        logging.error(f"### Error: {e} ###")
        send_error_to_line(os.getenv("LINE_MGMT_TOKEN_KEY"))

    # 何の対応が必要か判定
    try:
        goto_each_task(gcal, events)
    except Exception as e:
        logging.error(f"### Error: {e} ###")
        send_error_to_line(os.getenv("LINE_MGMT_TOKEN_KEY"))

    logging.info("#=== Program Finished ===#")


# Functions ------------------
def get_events_googlecal(gcal: CalendarApi) -> list:
    """
    Google カレンダーからスケジュールを取得する関数
    Args:
        gcal (CalendarApi): Google calendar class
    Returns:
        events (list): 2ヶ月以内の予定されたスケジュールのリスト
    """
    # Google Calendar クラスの呼び出し
    last_week = datetime.datetime.now(JST) + datetime.timedelta(days=-7)
    try:
        events = gcal.get(start_date=last_week, prior_days=90)  # 先週から60日後までのスケジュールを取得
    except EventNotFoundException as e:
        logging.error(f"{e}")
        return []

    return events


def goto_each_task(gcal: CalendarApi, events: list) -> None:
    """
    具体的なタスクに分岐
    Args:
        gcal (CalendarApi): Google calendar class
        events (list): スケジュールされた予定。タイトルと日付。
    Returns:
        None
    """
    today = datetime.date.today()
    for event in events:
        event_date = datetime.date.fromisoformat(re.search(r"^\d{4}-\d{2}-\d{2}", event["start"]["dateTime"]).group())
        if event_date - today == datetime.timedelta(days=1):
            # イベント前日
            pre_event_mgmt(event)
        elif today - event_date == datetime.timedelta(days=1):
            # イベント翌日
            post_event_mgmt(event, events, gcal)
        elif event_date - today == datetime.timedelta(days=7):
            # イベント1週間前
            one_week_pre_mgmt(event)
        else:
            pass


def one_week_pre_mgmt(event: dict) -> None:
    """
    イベントの1週間前のリマインド
    * {イベント内容}の1週間前です、と通知
    * 調整さんのURLを送り、参加者の確認を促す
    * （TRPG会なら）各卓のマスターに準備状況をフォローするよう依頼
    * Lineに通知する
    Args:
        event (dict): Google カレンダーのイベント情報
    Returns:
        None
    """
    line_text = f"{event['summary']} の1週間前です。\n"
    line_text += "現在の応募状況を確認して募集を行ってください。\n"
    line_text += detect_remove_a_tag(event["description"]) + "\n"
    if "TRPG" in event["summary"]:
        line_text += "各卓のマスターに準備状況を確認してください。\n"
    # LINE 通知
    send_line_notify(line_text, os.getenv("LINE_MGMT_TOKEN_KEY"))
    return None


def pre_event_mgmt(event: dict) -> None:
    """
    イベントの前日に行うタスク
    * 明日は{イベント内容}です、と通知
    * 集合時間が12:30で間違いないか確認を促す
    * 調整さんのURLを送り、参加者の確認を促す
    * （TRPG会なら）次々回のTRPGの卓内容を考えるようにリマインド
    * Lineに通知する
    Args:
        event (dict): Google カレンダーのイベント情報
    Returns:
        None
    """
    line_text = f"明日は {event['summary']} です。\n"
    line_text += "集合時間は12:30です。\n"
    line_text += "今回の調整さんURLはこちら\n"
    line_text += detect_remove_a_tag(event["description"]) + "\n"
    if "TRPG" in event["summary"]:
        line_text += "次々回の卓内容も考えて宣伝できるようにしておきましょう。\n"
    # LINE 通知
    send_line_notify(line_text, os.getenv("LINE_MGMT_TOKEN_KEY"))
    return None


def post_event_mgmt(event: dict, events: list, gcal: CalendarApi) -> None:
    """
    ボドゲ会の翌日に行うタスク
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
    """
    # 今回の精算
    line_text = f"{event['summary']} お疲れ様でした。どうでしたか？^^\n"
    line_text += "参加者を確認し、帳簿を更新してください。備品やお菓子代などの金額も入れてください。\n"
    line_text += os.getenv("LUXY_BDG_ACC_BOOK") + "\n"
    line_text += "今回の参加者はこちらです。\n"
    line_text += detect_remove_a_tag(event["description"]) + "\n"
    send_line_notify(line_text, os.getenv("LINE_MGMT_TOKEN_KEY"))

    # 次回の案内
    next_event = get_next_event(event, events)
    next_event_date = datetime.date.fromisoformat(
        re.search(r"^\d{4}-\d{2}-\d{2}", next_event["start"]["dateTime"]).group()
    )
    line_text = f"次回は {next_event_date} 予定です。会議室の予約をお願いします。\n"
    line_text += "調整さんの周知をお願いします。\n"
    if "description" in next_event:
        line_text += detect_remove_a_tag(next_event["description"])
    else:
        choseisan_url = make_choseisan(next_event)
        next_event["description"] = choseisan_url
        gcal.update(next_event)
        line_text += choseisan_url

    # LINE 通知
    send_line_notify(line_text, os.getenv("LINE_MGMT_TOKEN_KEY"))

    # 今後の予定の案内
    post_event_list = get_post_event_list(events)
    line_text = "今後の予定一覧です。\n"
    for event in post_event_list:
        line_text += f"{event['date']}({event['date'].strftime('%a')}): {event['title']}\n"

    # LINE 通知
    # send_line_notify(line_text, os.getenv("LINE_USER_TOKEN_KEY"))
    send_line_notify(line_text, os.getenv("LINE_MGMT_TOKEN_KEY"))
    return None


def get_next_event(last_event: dict, events: list) -> None:
    """
    次回の同一イベントを取得するメソッド
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
        events (list): Googleカレンダーから取得した直近の予定一覧
    Returns:
        event (dict): 次回のイベント
    """
    # Fix the event type
    last_event_type = detect_event_type(last_event)
    last_event_date = datetime.date.fromisoformat(
        re.search(r"^\d{4}-\d{2}-\d{2}", last_event["start"]["dateTime"]).group()
    )
    for event in events:
        event_date = datetime.date.fromisoformat(re.search(r"^\d{4}-\d{2}-\d{2}", event["start"]["dateTime"]).group())
        event_type = detect_event_type(event)
        if event_date - last_event_date <= datetime.timedelta(days=0):
            continue
        elif last_event_type == event_type:
            return event
    return {}


def detect_remove_a_tag(description: str) -> str:
    """
    detect & remove HTML a tag.
    Args:
        description (str): the target strings.
    Return:
        str: a pure strings.
    """
    regex = re.search(r"^<a .+>(.+)</a>", description)
    if regex:
        return regex.group(1)
    else:
        return description


def get_post_event_list(events: list) -> list:
    """
    数か月先のイベント一覧を取得するメソッド
    Args:
        events (list): Googleカレンダーから取得した直近の予定一覧
    Returns:
        post_events (list): 予定の日付一覧
    """
    upper_limit_date = (datetime.date.today() + datetime.timedelta(days=93)).replace(day=1)
    post_events = []
    for event in events:
        post_event = {
            "date": datetime.date.fromisoformat(re.search(r"^\d{4}-\d{2}-\d{2}", event["start"]["dateTime"]).group()),
            "title": event["summary"],
        }
        if post_event["date"] - datetime.date.today() <= datetime.timedelta(days=0):
            continue
        elif post_event["date"] > upper_limit_date:
            break
        post_events.append(post_event)
    return post_events


def send_error_to_line(line_notify_token: str) -> None:
    message = "何らかのエラーが発生したようです。ログを確認してください。"
    send_line_notify(message, line_notify_token)


# Main ---


if __name__ == "__main__":
    auto_task_notifier_main()
