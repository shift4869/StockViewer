import asyncio
from logging import INFO, getLogger
from pathlib import Path
import re
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from db import StockViewer, ExchangeRate, engine, Base
from ExchangeRateFetcher import ExchangeRateFetcher

logger = getLogger(__name__)
logger.setLevel(INFO)


class StockSaver():
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def upsert_exchange_rate(self) -> float | None:
        # 現在の米ドル/円を取得する
        sf = ExchangeRateFetcher()
        rate_dict = sf.get_rate()
        match rate_dict:
            case {
                "target": target,
                "base": base,
                "rate": rate,
                "date": date,
            }:
                fetched_date_format = "%m/%d %H:%M"
                fetched_datetime = datetime.strptime(date, fetched_date_format)
                fetched_datetime = fetched_datetime.replace(year=datetime.now().year)
                isodatetime = fetched_datetime.isoformat()
                params_dict = {
                    "target": target,
                    "base": base,
                    "rate": rate,
                    "created_at": isodatetime,
                    "updated_at": datetime.now().isoformat(),
                }
                record = ExchangeRate.create(params_dict)

                # レコードUPSERT
                Session = sessionmaker(engine)
                session = Session()

                q = session.query(ExchangeRate).filter_by(target=target, base=base, rate=rate, created_at=isodatetime)
                p = q.first()
                if not p:
                    session.add(record)
                else:
                    p.target = params_dict.get("target")
                    p.base = params_dict.get("base")
                    p.rate = params_dict.get("rate")
                    p.created_at = params_dict.get("created_at")
                    p.updated_at = params_dict.get("updated_at")
                session.commit()
                session.close()
                return float(rate)
        return None

    def insert_table(self, table_data):
        # ポートフォリオデータを整形してテーブルに格納する

        # 現在の為替レートを取得してDBに格納
        self.rate = self.upsert_exchange_rate()
        if not self.rate:
            self.rate = 1.0

        records = []
        for row_list in table_data:
            # 数値の区切りのカンマを取り除く
            row_list = [str(r).replace(",", "") for r in row_list]

            # 銘柄名項目からコードと銘柄名を分離する
            code_name = str(row_list[2])
            if re.findall("^.*\xa0.*$", code_name):
                code = code_name.split("\xa0", 1)[0]
                name = code_name.split("\xa0", 1)[1]
            else:
                # 投資信託はコードがない
                code = ""
                name = code_name

            # 銘柄名のスペースを削除
            name = name.replace("\xa0", "")
            # 銘柄名の\u3000を全角空白に置き換える
            name = name.replace("\\u3000", "　")

            # 銘柄タイプと海外株かどうかを設定する
            stock_type = "不明"
            is_foreign = False
            if re.findall("^\d+$", code):
                # 銘柄コードが数字なら特定預りの国内株
                stock_type = "特定預り"
                is_foreign = False
            elif re.findall("^[A-Z]+$", code):
                # 銘柄コードがアルファベットなら一般預りの海外株
                stock_type = "一般預り"
                is_foreign = True
            elif code == "":
                # 銘柄コードが空なら積み立てNISA
                stock_type = "つみたてNISA預り"
                is_foreign = False
            else:
                # それ以外
                stock_type = "不明"
                is_foreign = False

            # 海外株なら為替レートを反映させる
            rate = self.rate if is_foreign else 1.0

            # 値の設定
            purchased_at = row_list[3]
            amount = int(row_list[4])
            unit_value = float(row_list[6])
            current_value = float(row_list[7])
            profit_loss_value = float(row_list[10])
            profit_loss_ratio = float(row_list[11])
            eval_value = float(row_list[12])

            # 小数第3位で四捨五入
            def quamtize(v) -> float:
                d = Decimal(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                return float(d)
            unit_value_jpn = quamtize(unit_value * rate)
            current_value_jpn = quamtize(current_value * rate)
            profit_loss_value_jpn = quamtize(profit_loss_value * rate)
            eval_value_jpn = quamtize(eval_value * rate)

            # レコード作成
            row_dict = {
                "stock_type": stock_type,
                "is_foreign": is_foreign,
                "name": name,
                "code": code,
                "purchased_at": purchased_at,
                "amount": amount,
                "unit_value": unit_value,
                "unit_value_jpn": unit_value_jpn,
                "current_value": current_value,
                "current_value_jpn": current_value_jpn,
                "profit_loss_value": profit_loss_value,
                "profit_loss_value_jpn": profit_loss_value_jpn,
                "profit_loss_ratio": profit_loss_ratio,
                "eval_value": eval_value,
                "eval_value_jpn": eval_value_jpn,
            }
            records.append(StockViewer.create(row_dict))
        # print(result)

        # レコードTRUNCATE->INSERT
        Session = sessionmaker(engine)
        session = Session()
        session.execute("TRUNCATE TABLE StockViewer")
        for record in records:
            session.add(record)
        session.commit()
        session.close()
        pass


if __name__ == "__main__":
    from StockFetcher import StockFetcher
    sf = StockFetcher()
    content = None
    loop = asyncio.get_event_loop()
    content = loop.run_until_complete(sf.fetch())
    # with Path("./sample/content.html").open("r") as fin:
    #     content = fin.read()
    table_data = sf.parse_table(content)

    ss = StockSaver()
    result = ss.insert_table(table_data)
