import os
import datetime
from googleapiclient.discovery import build
from google.auth import load_credentials_from_file


class CalendarApi:
    def __init__(self):
        self.calendarId = os.getenv("CALENDAR_ID")

        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        gapi_creds = load_credentials_from_file(os.getenv("KEYJSONFILE"), SCOPES)[0]
        self.service = build("calendar", "v3", credentials=gapi_creds)

    def insert(self, body):
        result = self.service.events().insert(calendarId=self.calendarId, body=body).execute()
        return result

    def get(
        self,
        start_date: datetime = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9), "JST")),
        prior_days: int = 30,
    ) -> list:
        """
        Google カレンダーの予定を取得するメソッド
        Args:
            start_date (datetime): 予定取得開始日。初期値は現在。
            prior_days (int): 何日後までの予定を取得するか。default = 30
        Return:
            events (list): 取得した予定のリスト
        """
        # タイムゾーンAsia/Tokyoの生成
        JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")

        period = start_date + datetime.timedelta(days=prior_days)
        timeMax = datetime.datetime(period.year, period.month, period.day, 23, 59, tzinfo=JST)

        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendarId,
                timeMin=start_date.isoformat(),
                timeMax=timeMax.isoformat(),
                maxResults=90,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        if not events:
            raise EventNotFoundException
        return events

    def delete(self, event):
        self.service.events().delete(calendarId=self.calendarId, eventId=event["id"]).execute()

    def update(self, event):
        self.service.events().update(calendarId=self.calendarId, eventId=event["id"], body=event).execute()


class MyException(Exception):
    def __init__(self, arg=""):
        self.arg = arg


class EventNotFoundException(MyException):
    def __str__(self):
        return "No Events are found during the specified period."


class CalendarBody:
    def createInsertData(self, data):
        body = {
            "summary": data.summary,
            "description": data.description,
            "start": {
                "dateTime": datetime.datetime(data.year, data.month, data.day, data.hour, data.minute).isoformat(),
                "timeZone": "Japan",
            },
            "end": {
                "dateTime": datetime.datetime(data.year, data.month, data.day, data.hour + 1, data.minute).isoformat(),
                "timeZone": "Japan",
            },
        }
        return body
