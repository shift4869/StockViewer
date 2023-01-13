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

# logging.config.fileConfig("./log/logging.ini", disable_existing_loggers=False)
# for name in logging.root.manager.loggerDict:
#     # 自分以外のすべてのライブラリのログ出力を抑制
#     if "stockviewer" not in name:
#         getLogger(name).disabled = True
logger = getLogger(__name__)
logger.setLevel(INFO)


class StockFetcher():
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

    def parse_table(self, html_page_content) -> list[dict]:
        soup = BeautifulSoup(html_page_content, "html.parser")
        tables = soup.findAll("table", attrs={"bgcolor": "#9fbf99", "border": "0", "cellspacing": "1", "cellpadding": "4", "width": "100%"})
        table_data = []
        full_column_num = -1
        for table in tables:
            trs = table.findAll("tbody")[0].findAll("tr")
            prev_name_code = ""
            for tr in trs:
                tds = tr.findAll("td")

                # 1行取得
                buf = ""
                for td in tds:
                    buf = buf + "\t" + td.text if buf != "" else td.text

                # 銘柄が含まれているか確認
                code_name = ""
                column_list = re.split("[\t\n]", buf)

                # 表のキャプションはスキップ
                if column_list[0] == "取引":
                    full_column_num = len(column_list) + 2
                    continue

                # 銘柄が空白でないか確認
                # full_column_num = 13
                if len(column_list) == full_column_num:
                    code_name = column_list[2]
                    prev_name_code = code_name
                else:
                    code_name = prev_name_code
                    column_list = ["", "", code_name] + column_list

                table_data.append(column_list)

        return table_data


if __name__ == "__main__":
    sf = StockFetcher()
    content = None
    loop = asyncio.get_event_loop()
    content = loop.run_until_complete(sf.fetch())
    # with Path("./sample/content.html").open("r") as fin:
    #     content = fin.read()
    table_data = sf.parse_table(content)
    print(table_data)
