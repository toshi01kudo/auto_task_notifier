import logging
import sys
from dotenv import load_dotenv
import datetime
import os
import re
import time
from class_str_enum import EventIdStrEnum
from common_tools import detect_event_type
from selenium_helper import SeleniumBrowser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# import requests
# from __future__ import annotations
# from collections.abc import Iterable
# from dataclasses import dataclass
# from bs4 import BeautifulSoup
# from requests.sessions import Session
# from urllib.parse import urljoin


# Main ---
def make_choseisan_exec() -> str:
    """
    make_choseisanを実行するタスク
    引数からeventのdictを受け取って実行する
    Return:
        choseisan_url (str): 作成した調整さんのURL
    """
    # Logging
    logging.basicConfig(level=logging.INFO, format=" %(asctime)s - %(levelname)s - %(message)s")
    logging.info("#=== Start program ===#")

    if len(sys.argv) < 2:
        _help()
        sys.exit()
    elif len(sys.argv) == 2:
        event = sys.argv[1]
    else:
        logging.error("#=== Stop the process due to error. ===#")
        return ""

    # load parameters
    load_dotenv()

    return make_choseisan(event)


# Functions ---


def _help():
    print("Usage: python3 " + os.path.basename(__file__) + " ${event_dict}")


def make_choseisan(event: dict) -> str:
    """
    調整さんを作るタスク
    ボドゲ会は完全に作成、TRPG会は素案のみ作成
    文言はテンプレートから読み込み
    Args:
        event (dict): スケジュールされた予定。タイトルと日付。
    Returns:
        choseisan_url (str): 作成された調整さんのURL
    """
    event_date = datetime.date.fromisoformat(re.search(r"^\d{4}-\d{2}-\d{2}", event["start"]["dateTime"]).group())
    event_date_str = event_date.strftime("%Y/%m/%d")
    choseisan_title = f"{event['summary']} - {event_date_str}"
    event_type = detect_event_type(event)
    choseisan = Choseisan(email=os.getenv("CHOSEISAN_MAIL"), password=os.getenv("CHOSEISAN_PASS"))
    if event_type == EventIdStrEnum.BOARDGAME:
        three_days_before = event_date + datetime.timedelta(days=-3)
        with open("template_choseisan_bdg_comment.txt", "r", encoding="utf-8") as f:
            comment = (
                f.read()
                .replace("%%THREE_DAYS_BEFORE%%", three_days_before.strftime("%m/%d"))
                .replace("%%TONPY_TEL%%", os.getenv("TONPY_TEL"))
                .replace("%%TOSHI_TEL%%", os.getenv("TOSHI_TEL"))
            )
        return choseisan.create_event(
            title=choseisan_title, candidate_days=["13:00～ ゲーム会", "20:30〜 懇親会"], comment=comment
        )
    elif event_type == EventIdStrEnum.TRPG:
        with open("template_choseisan_trpg_comment.txt", "r", encoding="utf-8") as f:
            comment = f.read()
        return choseisan.create_event(title=choseisan_title, candidate_days=["Comming soon..."], comment=comment)
    choseisan.browser.close_selenium()


# Class ---


class Choseisan:
    def __init__(self, email: str, password: str) -> None:
        """
        initialize selenium browser during init process.
        Args:
            email: 調整さんのログインID
            password: 調整さんのログインパスワード
        """
        self.email = email
        self.password = password
        self.browser = SeleniumBrowser(
            geckodriver_path=os.getenv("GECKODRIVER_PATH"),
            browser_setting={
                "browser_path": os.getenv("FIREFOX_BINARY_PATH"),
                "browser_profile": os.getenv("FIREFOX_PROFILE_PATH"),
            },
        )
        self._login()

    def _login(self) -> None:
        url = "https://chouseisan.com/auth/login"
        self.browser.browser.get(url)

        # ページロード完了まで待機
        try:
            WebDriverWait(self.browser.browser, 10).until(EC.presence_of_element_located((By.NAME, "submit")))
        except TimeoutException as te:
            print(f"Error with timeout...: {te}")

        # ID
        e = self.browser.browser.find_element(By.NAME, "email")
        e.clear()
        e.send_keys(self.email)
        # PASS
        e = self.browser.browser.find_element(By.NAME, "password")
        e.clear()
        e.send_keys(self.password)

        # ログイン実行
        button = self.browser.browser.find_element(By.NAME, "submit")
        time.sleep(1)
        button.click()

    def goto_new_event_page(self) -> None:
        url = "https://chouseisan.com"
        self.browser.browser.get(url)

    def goto_userpage(self) -> None:
        url = "https://chouseisan.com/user"
        self.browser.browser.get(url)

    def create_event(
        self,
        title: str,
        candidate_days: list,
        comment: str = "",
    ) -> str:
        """Create event.
        Args:
            title(str): Title of the event
            candidate_days(list): Candidate days for the event
            comment(str): Comment about the event
        Returns:
            Event URL
        """
        self.goto_new_event_page()

        # ページロード完了まで待機
        try:
            WebDriverWait(self.browser.browser, 10).until(EC.presence_of_element_located((By.ID, "createBtn")))
        except TimeoutException as te:
            print(f"Error with timeout...: {te}")

        # Title
        e = self.browser.browser.find_element(By.NAME, "name")
        e.clear()
        e.send_keys(title)

        # Comment
        e = self.browser.browser.find_element(By.NAME, "comment")
        e.clear()
        e.send_keys(comment)

        # Candidates
        e = self.browser.browser.find_element(By.NAME, "kouho")
        e.clear()
        input_candidate_days = "\n".join(candidate_days)
        e.send_keys(input_candidate_days)

        # Create Event
        button = self.browser.browser.find_element(By.ID, "createBtn")
        time.sleep(1)
        button.click()

        # ページロード完了まで待機
        try:
            WebDriverWait(self.browser.browser, 10).until(EC.presence_of_element_located((By.ID, "listUrl")))
        except TimeoutException as te:
            print(f"Error with timeout...: {te}")

        # Event URL
        new_event_url = self.browser.browser.find_element(By.ID, "listUrl").get_attribute("value")
        return new_event_url


# Main ---


if __name__ == "__main__":
    make_choseisan_exec()
