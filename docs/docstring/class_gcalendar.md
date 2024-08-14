Module class_gcalendar
======================

Classes
-------

`CalendarApi()`
:   

    ### Methods

    `delete(self, event)`
    :

    `get(self, start_date: <module 'datetime' from '/opt/hostedtoolcache/Python/3.11.9/x64/lib/python3.11/datetime.py'> = datetime.datetime(2024, 8, 14, 15, 44, 6, 607726, tzinfo=datetime.timezone(datetime.timedelta(seconds=32400), 'JST')), prior_days: int = 30) ‑> list`
    :   Google カレンダーの予定を取得するメソッド
        Args:
            start_date (datetime): 予定取得開始日。初期値は現在。
            prior_days (int): 何日後までの予定を取得するか。default = 30
        Return:
            events (list): 取得した予定のリスト

    `insert(self, body)`
    :

    `update(self, event)`
    :

`CalendarBody()`
:   

    ### Methods

    `createInsertData(self, data)`
    :

`EventNotFoundException(arg='')`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * class_gcalendar.MyException
    * builtins.Exception
    * builtins.BaseException

`MyException(arg='')`
:   Common base class for all non-exit exceptions.

    ### Ancestors (in MRO)

    * builtins.Exception
    * builtins.BaseException

    ### Descendants

    * class_gcalendar.EventNotFoundException