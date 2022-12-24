from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
import mysql.connector

USER = "root"
PASSWORD = "root"
HOST = "localhost"
DATABASE = "stockviewer"

engine = create_engine(f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}/{DATABASE}")
Base = declarative_base()


class StockViewer(Base):
    __tablename__ = "StockViewer"
    __table_args__ = ({"mysql_charset": "utf8mb4"})
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=True)


def sample_db_controll():
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    session = Session()
    sv1 = StockViewer(name="銘柄1")
    sv2 = StockViewer(name="銘柄2")
    session.add(sv1)
    session.add(sv2)
    session.commit()


if __name__ == "__main__":
    pass
