"""
全体向け LINE グループへの予定一覧周知のテスト
"""

import datetime
import locale
import os
import unittest
from unittest import mock

import auto_task_notifier
from auto_task_notifier import Event
from class_gcalendar import EventNotFoundException

CHOSEISAN_URL = "https://chouseisan.com/s?h=0123456789abcdef0123456789abcdef"
CALENDAR_URL = "https://calendar.example.com/dummy"


def make_event(date: str, summary: str, description: str | None = None) -> Event:
    raw = {"summary": summary, "start": {"dateTime": f"{date}T13:00:00+09:00"}}
    if description is not None:
        raw["description"] = description
    return Event(raw)


class BuildScheduleAnnouncementTest(unittest.TestCase):
    def test_event_with_choseisan_url_is_listed_with_url_on_next_line(self):
        events = [make_event("2099-10-24", "T4 ボドゲ会", CHOSEISAN_URL)]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        self.assertEqual(text, f"・10/24 (土) T4 ボドゲ会\n{CHOSEISAN_URL}\n")

    def test_choseisan_url_wrapped_in_a_tag_is_extracted(self):
        description = f'<a href="{CHOSEISAN_URL}">{CHOSEISAN_URL}</a>'
        events = [make_event("2099-10-24", "T4 ボドゲ会", description)]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        self.assertEqual(text, f"・10/24 (土) T4 ボドゲ会\n{CHOSEISAN_URL}\n")

    def test_event_without_description_is_listed_with_date_only(self):
        events = [make_event("2099-11-15", "T4 ボドゲ会")]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        self.assertEqual(text, "・11/15 (日) T4 ボドゲ会\n")

    def test_description_without_choseisan_url_is_not_shown(self):
        events = [make_event("2099-11-15", "T4 ボドゲ会", "Comming soon...")]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        self.assertEqual(text, "・11/15 (日) T4 ボドゲ会\n")

    def test_only_events_from_today_to_end_of_month_after_next_are_listed(self):
        events = [
            make_event("2099-09-30", "過去の会"),
            make_event("2099-10-01", "当日の会"),
            make_event("2099-12-31", "翌々月末の会"),
            make_event("2100-01-01", "3か月後の会"),
        ]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        self.assertEqual(text, "・10/1 (木) 当日の会\n・12/31 (木) 翌々月末の会\n")

    def test_range_crosses_year_end(self):
        events = [
            make_event("2100-01-31", "翌々月末の会"),
            make_event("2100-02-01", "3か月後の会"),
        ]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 11, 15), None)
        self.assertEqual(text, "・1/31 (日) 翌々月末の会\n")

    def test_weekday_is_japanese_regardless_of_locale(self):
        saved = locale.setlocale(locale.LC_TIME)
        self.addCleanup(locale.setlocale, locale.LC_TIME, saved)
        locale.setlocale(locale.LC_TIME, "C")
        # 2099-10-05 は月曜日。そこから7日分で 月〜日 を一巡する
        events = [make_event(f"2099-10-{day:02d}", "会") for day in range(5, 12)]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        weekdays = [line.split("(")[1].split(")")[0] for line in text.splitlines()]
        self.assertEqual(weekdays, ["月", "火", "水", "木", "金", "土", "日"])

    def test_calendar_footer_is_appended_when_calendar_url_is_given(self):
        events = [make_event("2099-11-15", "T4 ボドゲ会")]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), CALENDAR_URL)
        self.assertEqual(
            text,
            "・11/15 (日) T4 ボドゲ会\n"
            "--\n"
            "開催予定のカレンダーはこちら（3ヶ月以降は予告なく変更になる可能性があります）\n"
            f"{CALENDAR_URL}\n",
        )

    def test_no_events_in_range_gives_empty_text_even_with_calendar_url(self):
        events = [make_event("2100-01-01", "3か月後の会")]
        text = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), CALENDAR_URL)
        self.assertEqual(text, "")


USER_GROUP_ID = "dummy-user-group"
MGMT_GROUP_ID = "dummy-mgmt-group"
DEMO_GROUP_ID = "dummy-demo-group"


class NotifyScheduleToUsersTest(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch("auto_task_notifier.send_line_masageapi")
        self.send = patcher.start()
        self.addCleanup(patcher.stop)

    def test_announcement_is_sent_to_user_group(self):
        events = [make_event("2099-11-15", "T4 ボドゲ会")]
        env = {"LINE_MESSAGE_API_GROUP_ID_USER": USER_GROUP_ID, "CALENDAR_PUBLIC_URL": CALENDAR_URL}
        with mock.patch.dict(os.environ, env, clear=True):
            auto_task_notifier.notify_schedule_to_users(events, datetime.date(2099, 10, 1))
        expected = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), CALENDAR_URL)
        self.send.assert_called_once_with(expected, USER_GROUP_ID)

    def test_nothing_is_sent_when_user_group_id_is_not_set(self):
        events = [make_event("2099-11-15", "T4 ボドゲ会")]
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertLogs(level="ERROR"):
                auto_task_notifier.notify_schedule_to_users(events, datetime.date(2099, 10, 1))
        self.send.assert_not_called()

    def test_demo_mode_sends_to_demo_group_without_user_group_id(self):
        events = [make_event("2099-11-15", "T4 ボドゲ会")]
        env = {"DEMO_MODE": "1", "LINE_MESSAGE_API_GROUP_ID_DEMO": DEMO_GROUP_ID}
        with mock.patch.dict(os.environ, env, clear=True):
            auto_task_notifier.notify_schedule_to_users(events, datetime.date(2099, 10, 1))
        expected = auto_task_notifier.build_schedule_announcement(events, datetime.date(2099, 10, 1), None)
        self.send.assert_called_once_with(expected, DEMO_GROUP_ID)

    def test_nothing_is_sent_when_no_events_in_range(self):
        events = [make_event("2100-01-01", "3か月後の会")]
        with mock.patch.dict(os.environ, {"LINE_MESSAGE_API_GROUP_ID_USER": USER_GROUP_ID}, clear=True):
            auto_task_notifier.notify_schedule_to_users(events, datetime.date(2099, 10, 1))
        self.send.assert_not_called()


class ScheduleTriggerTest(unittest.TestCase):
    """CalendarApi と LINE 送信を差し替えて、全体向けグループへの送信有無だけを観測する"""

    def calls_to_user_group(self, main_func, today: datetime.date, event_date: str = "2099-11-15") -> list:
        event = make_event(event_date, "T4 ボドゲ会")

        def fake_get(start_date: datetime.datetime, prior_days: int) -> list:
            """実 API と同じく、取得期間内の予定だけを返し、無ければ例外を送出する"""
            last_date = start_date.date() + datetime.timedelta(days=prior_days)
            if not start_date.date() <= event.date <= last_date:
                raise EventNotFoundException
            return [event.raw]

        env = {"LINE_MESSAGE_API_GROUP_ID_MGMT": MGMT_GROUP_ID, "LINE_MESSAGE_API_GROUP_ID_USER": USER_GROUP_ID}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            mock.patch("auto_task_notifier.load_dotenv"),
            mock.patch("auto_task_notifier.CalendarApi") as gcal_cls,
            mock.patch("auto_task_notifier.send_line_masageapi") as send,
        ):
            gcal_cls.return_value.get.side_effect = fake_get
            main_func(today=today)
        return [call for call in send.call_args_list if call.args[1] == USER_GROUP_ID]

    def test_daily_run_sends_announcement_on_first_day_of_month(self):
        calls = self.calls_to_user_group(auto_task_notifier.auto_task_notifier_main, datetime.date(2099, 10, 1))
        self.assertEqual(len(calls), 1)
        self.assertIn("・11/15 (日) T4 ボドゲ会", calls[0].args[0])

    def test_daily_run_does_not_send_announcement_on_other_days(self):
        calls = self.calls_to_user_group(auto_task_notifier.auto_task_notifier_main, datetime.date(2099, 10, 2))
        self.assertEqual(calls, [])

    def test_manual_run_sends_announcement_on_any_day(self):
        calls = self.calls_to_user_group(auto_task_notifier.notify_schedule_main, datetime.date(2099, 10, 2))
        self.assertEqual(len(calls), 1)
        self.assertIn("・11/15 (日) T4 ボドゲ会", calls[0].args[0])

    def test_daily_run_fetches_events_up_to_end_of_month_after_next(self):
        main_func = auto_task_notifier.auto_task_notifier_main
        calls = self.calls_to_user_group(main_func, datetime.date(2099, 10, 1), event_date="2099-12-31")
        self.assertEqual(len(calls), 1)
        self.assertIn("・12/31 (木) T4 ボドゲ会", calls[0].args[0])

    def test_manual_run_fetches_events_up_to_end_of_month_after_next(self):
        main_func = auto_task_notifier.notify_schedule_main
        calls = self.calls_to_user_group(main_func, datetime.date(2099, 10, 1), event_date="2099-12-31")
        self.assertEqual(len(calls), 1)
        self.assertIn("・12/31 (木) T4 ボドゲ会", calls[0].args[0])


if __name__ == "__main__":
    unittest.main()
