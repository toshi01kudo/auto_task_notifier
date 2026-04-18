"""
This is main function to manage this repogitory.
"""

import argparse
import logging
from dotenv import load_dotenv
import datetime
import os
import re
import locale
from class_gcalendar import CalendarApi, EventNotFoundException
from class_str_enum import EventIdStrEnum
from make_choseisan import make_choseisan
from common_tools import detect_event_type, send_line_masageapi

# Parameters ------------------
JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
DATE_FORMATS_HINT = "YYYY-MM-DD, YYYYMMDD, YYYY/MM/DD, YYYY.MM.DD"
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


# Classes ------------------


class Event:
    """Google Calendar イベントのラッパー"""

    def __init__(self, raw: dict) -> None:
        self.raw = raw

    @property
    def summary(self) -> str:
        return self.raw["summary"]

    @property
    def date(self) -> datetime.date:
        start = self.raw.get("start", {})
        start_value = start.get("dateTime") or start.get("date")
        if start_value is None:
            raise ValueError("Event start is missing both 'dateTime' and 'date'")
        match = re.search(r"^\d{4}-\d{2}-\d{2}", start_value)
        if match is None:
            raise ValueError(f"Event start value is not a valid ISO date: {start_value!r}")
        return datetime.date.fromisoformat(match.group())

    @property
    def event_type(self) -> EventIdStrEnum:
        return detect_event_type(self.raw)

    @property
    def description(self) -> str | None:
        return self.raw.get("description")

    @description.setter
    def description(self, value: str | None) -> None:
        self.raw["description"] = value

    @property
    def clean_description(self) -> str:
        """HTMLのaタグを除去した説明文を返す"""
        if self.description is None:
            return ""
        return detect_remove_a_tag(self.description)

    def is_trpg(self) -> bool:
        return "TRPG" in self.summary

    def days_from_today(self) -> int:
        """今日からの日数差を返す（未来なら正、過去なら負）"""
        return (self.date - datetime.date.today()).days


class EventNotifier:
    """イベントに応じたLINE通知を管理する"""

    def __init__(self, gcal: CalendarApi, group_id: str) -> None:
        self.gcal = gcal
        self.group_id = group_id

    def notify(self, message: str) -> None:
        send_line_masageapi(message, self.group_id)

    def process_events(self, events: list[Event]) -> None:
        """全イベントを走査し、該当するタスクを実行する"""
        for event in events:
            days = event.days_from_today()
            if days == 1:
                self.on_pre_event(event)
            elif days == -1:
                self.on_post_event(event, events)
            elif days == 7:
                self.on_one_week_before(event)

    def on_one_week_before(self, event: Event) -> None:
        """イベント1週間前のリマインド"""
        text = f"{event.summary} の1週間前です。\n"
        text += "現在の応募状況を確認して募集を行ってください。\n"
        text += event.clean_description + "\n"
        if event.is_trpg():
            text += "各卓のマスターに準備状況を確認してください。\n"
        self.notify(text)

    def on_pre_event(self, event: Event) -> None:
        """イベント前日のタスク"""
        text = f"明日は {event.summary} です。\n"
        text += "集合時間は12:30です。\n"
        text += "今回の調整さんURLはこちら\n"
        text += event.clean_description + "\n"
        if event.is_trpg():
            text += "次々回の卓内容も考えて宣伝できるようにしておきましょう。\n"
        self.notify(text)

    def on_post_event(self, event: Event, all_events: list[Event]) -> None:
        """イベント翌日のタスク"""
        # 今回の精算
        text = f"{event.summary} お疲れ様でした。どうでしたか？^^\n"
        text += "参加者を確認し、帳簿を更新してください。備品やお菓子代などの金額も入れてください。\n"
        text += (os.getenv("LUXY_BDG_ACC_BOOK") or "") + "\n"
        text += "今回の参加者はこちらです。\n"
        text += event.clean_description + "\n"
        self.notify(text)

        # 次回の案内
        self._notify_next_event(event, all_events)

        # 今後の予定一覧
        self._notify_upcoming_events(all_events)

    def _notify_next_event(self, current: Event, all_events: list[Event]) -> None:
        """次回の同一タイプイベントを案内する"""
        next_ev = self._find_next_same_type(current, all_events)
        if next_ev is None:
            logging.warning(f"次回の {current.event_type} イベントが見つかりませんでした。")
            return
        text = f"次回は {next_ev.date} 予定です。会議室の予約をお願いします。\n"
        text += "調整さんの周知をお願いします。\n"
        if next_ev.description is not None:
            text += next_ev.clean_description
        else:
            choseisan_url = create_choseisan_for_event(self.gcal, next_ev)
            text += choseisan_url
        self.notify(text)

    def _notify_upcoming_events(self, all_events: list[Event]) -> None:
        """今後の予定一覧を通知する"""
        upper_limit = (datetime.date.today() + datetime.timedelta(days=93)).replace(day=1)
        text = "今後の予定一覧です。\n"
        for ev in all_events:
            if ev.days_from_today() <= 0:
                continue
            if ev.date > upper_limit:
                break
            text += f"{ev.date}({ev.date.strftime('%a')}): {ev.summary}\n"
        self.notify(text)

    @staticmethod
    def _find_next_same_type(current: Event, all_events: list[Event]) -> Event | None:
        """次回の同一タイプイベントを探す"""
        for ev in all_events:
            if ev.date <= current.date:
                continue
            if ev.event_type == current.event_type:
                return ev
        return None


# Functions ------------------


def create_choseisan_for_event(gcal: CalendarApi, event: Event) -> str:
    """指定イベントの調整さんを作成し、Google カレンダーに URL を登録する"""
    choseisan_url = make_choseisan(event.raw)
    event.description = choseisan_url
    gcal.update(event.raw)
    logging.info(f"調整さんを作成しました: {event.summary} ({event.date}) -> {choseisan_url}")
    return choseisan_url


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


def send_error_to_line(line_group_id: str) -> None:
    message = "何らかのエラーが発生したようです。ログを確認してください。"
    send_line_masageapi(message, line_group_id)


# Main ---


def auto_task_notifier_main() -> None:
    """
    スケジュールから自動的にタスクを通知するプログラム
    """
    # Logging
    logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")
    logging.info("#=== Start program ===#")

    # load parameters
    load_dotenv()

    group_id = os.getenv("LINE_MESSAGE_API_GROUP_ID_MGMT")
    if not group_id:
        logging.error("LINE_MESSAGE_API_GROUP_ID_MGMT is not set.")
        return

    # スケジュールを取得
    try:
        gcal = CalendarApi()
        last_week = datetime.datetime.now(JST) + datetime.timedelta(days=-7)
        raw_events = gcal.get(start_date=last_week, prior_days=90)
        events = [Event(e) for e in raw_events]
    except EventNotFoundException as e:
        logging.error(f"{e}")
        events = []
    except Exception as e:
        logging.error(f"### Error: {e} ###")
        send_error_to_line(group_id)
        logging.info("#=== Program Finished ===#")
        return

    # 何の対応が必要か判定
    try:
        notifier = EventNotifier(gcal, group_id)
        notifier.process_events(events)
    except Exception as e:
        logging.error(f"### Error: {e} ###")
        send_error_to_line(group_id)

    logging.info("#=== Program Finished ===#")


def create_choseisan_by_date_main(target_date_str: str) -> None:
    """指定日のイベントに対して調整さんを作成し、Google カレンダーに URL を登録する"""
    logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")
    logging.info("#=== Start create_choseisan_by_date ===#")

    load_dotenv()

    try:
        stripped = target_date_str.strip()
        normalized = re.sub(r"[/.]", "-", stripped)
        if re.fullmatch(r"\d{8}", normalized):
            normalized = f"{normalized[:4]}-{normalized[4:6]}-{normalized[6:]}"
        target_date = datetime.date.fromisoformat(normalized)
    except ValueError:
        logging.error(
            f"日付の形式が不正です: {target_date_str} ({DATE_FORMATS_HINT} で指定してください)"
        )
        return

    try:
        gcal = CalendarApi()
        target_datetime = datetime.datetime(target_date.year, target_date.month, target_date.day, tzinfo=JST)
        raw_events = gcal.get(start_date=target_datetime, prior_days=0)
        events = [Event(e) for e in raw_events]
    except EventNotFoundException:
        logging.error(f"{target_date} にイベントが見つかりませんでした。")
        return
    except Exception as e:
        logging.error(f"### Error: {e} ###")
        return

    # 指定日のイベントを検索
    matched = []
    for ev in events:
        try:
            if ev.date == target_date:
                matched.append(ev)
        except ValueError as e:
            logging.warning(f"イベントの日付取得をスキップしました: {e}")
    if not matched:
        logging.error(f"{target_date} にイベントが見つかりませんでした。")
        return

    for event in matched:
        if event.description is not None:
            logging.info(f"スキップ: {event.summary} ({event.date}) は既に説明が登録されています。")
            continue
        try:
            create_choseisan_for_event(gcal, event)
        except Exception as e:
            logging.error(f"調整さんの作成に失敗しました: {event.summary} ({event.date}) - {e}")

    logging.info("#=== Program Finished ===#")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Task Notifier")
    parser.add_argument(
        "--create-choseisan",
        metavar="DATE",
        help=f"指定日のイベントに対して調整さんを作成する ({DATE_FORMATS_HINT})",
    )
    args = parser.parse_args()

    if args.create_choseisan:
        create_choseisan_by_date_main(args.create_choseisan)
    else:
        auto_task_notifier_main()
