from logging import INFO, getLogger
from sqlalchemy.orm import sessionmaker

from db import StockViewer, engine, Base

logger = getLogger(__name__)
logger.setLevel(INFO)


class StockLoader():
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def select_table(self):
        # レコードSELECT
        Session = sessionmaker(engine)
        session = Session()
        records = session.query(StockViewer).all()
        session.close()
        return records


if __name__ == "__main__":
    sl = StockLoader()
    result = sl.select_table()
    print(result)
