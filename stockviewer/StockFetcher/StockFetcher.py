import configparser
import os
from pathlib import Path
import sys
from logging import INFO, getLogger
from pyppeteer import launch
from requests_html import HTML
import asyncio
import random
import logging.config
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

# logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
# for name in logging.root.manager.loggerDict:
#     # 自分以外のすべてのライブラリのログ出力を抑制
#     if "stockviewer" not in name:
#         getLogger(name).disabled = True
logger = getLogger(__name__)
logger.setLevel(INFO)


class StockFetcher():
    CONFIG_FILE_NAME = "./config/config.ini"

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
        """SBI証券のポートフォリオページを取得する
        """
        session = AsyncHTMLSession()
        browser = await launch(
            headless=True,
            # ignoreDefaultArgs=True,
            args=["--disable-gpu", "--user-data-dir=/tmp", "--no-sandbox"]
        )
        session._browser = browser
        page = await browser.newPage()

        # 対象ページに移動
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

        # ポートフォリオの画面に遷移
        selector = 'img[title="ポートフォリオ"]'
        await asyncio.gather(page.click(selector), page.waitForNavigation())

        content = await page.content()
        html = HTML(session=session, html=content, default_encoding="ja_JP.utf8")
        # await html.arender()

        await browser.close()

        return content

    def make_table_data(self, html_page_content):
        soup = BeautifulSoup(html_page_content, "html.parser")
        tables = soup.findAll("table", attrs={"bgcolor": "#9fbf99", "border": "0", "cellspacing": "1", "cellpadding": "4", "width": "100%"})
        for table in tables:
            trs = table.findAll("tbody")[0].findAll("tr")
            for tr in trs:
                # tds = tr.findAll("td", class_="mtext", attrs={"align": "left"})
                tds = tr.findAll("td")
                for td in tds:
                    print(td.text)
        pass


if __name__ == "__main__":
    sf = StockFetcher()
    content = None
    # loop = asyncio.get_event_loop()
    # content = loop.run_until_complete(sf.fetch())
    with Path("./stockviewer/sample/content.html").open("r") as fin:
        content = fin.read()
    table_data = sf.make_table_data(content)
