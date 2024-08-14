Module make_choseisan
=====================

Functions
---------

`make_choseisan(event: dict) ‑> str`
:   調整さんを作るタスク
    ボドゲ会は完全に作成、TRPG会は素案のみ作成
    文言はテンプレートから読み込み
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
    Returns:
        choseisan_url (str): 作成された調整さんのURL

`make_choseisan_exec() ‑> str`
:   make_choseisanを実行するタスク
    引数からeventのdictを受け取って実行する
    Return:
        choseisan_url (str): 作成した調整さんのURL

Classes
-------

`Choseisan(email: str, password: str)`
:   initialize selenium browser during init process.
    Args:
        email: 調整さんのログインID
        password: 調整さんのログインパスワード

    ### Methods

    `create_event(self, title: str, candidate_days: list, comment: str = '') ‑> str`
    :   Create event.
        Args:
            title(str): Title of the event
            candidate_days(list): Candidate days for the event
            comment(str): Comment about the event
        Returns:
            Event URL

    `goto_new_event_page(self) ‑> None`
    :

    `goto_userpage(self) ‑> None`
    :