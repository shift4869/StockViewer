from bs4 import BeautifulSoup
from logging import INFO, getLogger
from pathlib import Path
from pyppeteer import launch
from requests_html import AsyncHTMLSession
from requests_html import HTML
import asyncio
import configparser
import logging.config
import os
import random
import re
import sys

logger = getLogger(__name__)
logger.setLevel(INFO)


class ExchangeRateFetcher():
    CONFIG_FILE_NAME = "../config/config.ini"

    def __init__(self):
        self.config = configparser.ConfigParser()
        try:
            if not self.config.read(self.CONFIG_FILE_NAME, encoding="utf8"):
                raise IOError

            config = self.config["stock"]
            self.username = config["username"]
            self.password = config["password"]
        except Exception:
            error_message = "unknown error."
            logger.exception(error_message)
            exit(-1)

    async def fetch(self):
        """SBI証券の口座管理->口座(外貨建)ページにある米ドル/円を取得する
        """
        session = AsyncHTMLSession()
        browser = await launch(
            headless=True,
            # ignoreDefaultArgs=True,
            args=["--disable-gpu", "--user-data-dir=/tmp", "--no-sandbox"]
        )
        session._browser = browser
        page = await browser.newPage()

        # トップページに移動
        url = "https://www.sbisec.co.jp/ETGate"

        # ページ遷移して読み込みが終わるまで待つ
        await asyncio.gather(
            page.goto(url),
            page.waitForNavigation(),
        )

        # contentを取得し、request-htmlのparserで読み込み
        content = await page.content()
        html = HTML(session=session, html=content, default_encoding="utf-8")

        # ログイン
        await page.waitFor(random.random() * 3 * 1000)
        selector = 'input[name="user_id"]'
        await page.type(selector, self.username)
        await page.waitFor(random.random() * 3 * 1000)
        selector = 'input[name="user_password"]'
        await page.type(selector, self.password)
        await page.waitFor(random.random() * 3 * 1000)
        selector = 'input[name="ACT_login"]'
        await asyncio.gather(page.click(selector), page.waitForNavigation())

        # contentを取得し、request-htmlのparserで読み込み
        await page.waitForNavigation()
        content = await page.content()

        # 口座管理のページに遷移
        selector = 'img[title="口座管理"]'
        await asyncio.gather(page.click(selector), page.waitForNavigation())

        # 口座(外貨建)のページに遷移
        selector = 'a[href="/ETGate/?_ControlID=WPLETsmR001Control&_DataStoreID=DSWPLETsmR001Control&_PageID=WPLETsmR001Sdtl12&sw_page=BondFx&sw_param2=02_201&cat1=home&cat2=none&getFlg=on"]'
        await asyncio.gather(page.click(selector), page.waitForNavigation())

        content = await page.content()
        html = HTML(session=session, html=content, default_encoding="ja_JP.utf8")
        # await html.arender()

        await browser.close()

        return content

    def parse_html(self, html_page_content) -> dict:
        soup = BeautifulSoup(html_page_content, "html.parser")
        trs = soup.findAll("tr", attrs={"class": "mtext", "valign": "top"})
        for tr in trs:
            tds = tr.findAll("td")
            row = [td.text for td in tds]
            if row[0] == "米ドル/円":
                rate = row[1]
                date = row[2][1:-1]  # 両端はカッコなので省く
                return {
                    "target": "USD",
                    "base": "JPN",
                    "rate": rate,
                    "date": date,
                }
        return {}

    def get_rate(self) -> dict:
        content = None
        loop = asyncio.get_event_loop()
        content = loop.run_until_complete(self.fetch())
        # with Path("./sample/exchange_rate.html").open("r") as fin:
        #     content = fin.read()
        result = self.parse_html(content)
        return result


if __name__ == "__main__":
    sf = ExchangeRateFetcher()
    print(sf.get_rate())
