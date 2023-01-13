from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, REAL, Boolean
import mysql.connector
from datetime import datetime

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
    stock_type = Column(String(30), nullable=True)
    is_foreign = Column(Boolean, nullable=True)
    code = Column(String(30), nullable=True)
    name = Column(String(256), nullable=True)
    purchased_at = Column(String(30), nullable=True)
    amount = Column(Integer, nullable=True)
    unit_value = Column(REAL, nullable=True)
    unit_value_jpn = Column(REAL, nullable=True)
    current_value = Column(REAL, nullable=True)
    current_value_jpn = Column(REAL, nullable=True)
    profit_loss_value = Column(REAL, nullable=True)
    profit_loss_value_jpn = Column(REAL, nullable=True)
    profit_loss_ratio = Column(REAL, nullable=True)
    eval_value = Column(REAL, nullable=True)
    eval_value_jpn = Column(REAL, nullable=True)
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)

    def __init__(self,
                 stock_type,
                 is_foreign,
                 code,
                 name,
                 purchased_at,
                 amount,
                 unit_value,
                 unit_value_jpn,
                 current_value,
                 current_value_jpn,
                 profit_loss_value,
                 profit_loss_value_jpn,
                 profit_loss_ratio,
                 eval_value,
                 eval_value_jpn,
                 created_at=datetime.now().isoformat(),
                 updated_at=datetime.now().isoformat()) -> None:
        self.stock_type = stock_type
        self.is_foreign = is_foreign
        self.code = code
        self.name = name
        self.purchased_at = purchased_at
        self.amount = amount
        self.unit_value = unit_value
        self.unit_value_jpn = unit_value_jpn
        self.current_value = current_value
        self.current_value_jpn = current_value_jpn
        self.profit_loss_value = profit_loss_value
        self.profit_loss_value_jpn = profit_loss_value_jpn
        self.profit_loss_ratio = profit_loss_ratio
        self.eval_value = eval_value
        self.eval_value_jpn = eval_value_jpn
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "stock_type": self.stock_type,
            "is_foreign": self.is_foreign,
            "code": self.code,
            "name": self.name,
            "purchased_at": self.purchased_at,
            "amount": self.amount,
            "unit_value": self.unit_value,
            "unit_value_jpn": self.unit_value_jpn,
            "current_value": self.current_value,
            "current_value_jpn": self.current_value_jpn,
            "profit_loss_value": self.profit_loss_value,
            "profit_loss_value_jpn": self.profit_loss_value_jpn,
            "profit_loss_ratio": self.profit_loss_ratio,
            "eval_value": self.eval_value,
            "eval_value_jpn": self.eval_value_jpn,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def create(cls, params_dict: dict) -> "StockViewer":
        return cls(
            stock_type=params_dict.get("stock_type"),
            is_foreign=params_dict.get("is_foreign"),
            code=params_dict.get("code"),
            name=params_dict.get("name"),
            purchased_at=params_dict.get("purchased_at"),
            amount=params_dict.get("amount"),
            unit_value=params_dict.get("unit_value"),
            unit_value_jpn=params_dict.get("unit_value_jpn"),
            current_value=params_dict.get("current_value"),
            current_value_jpn=params_dict.get("current_value_jpn"),
            profit_loss_value=params_dict.get("profit_loss_value"),
            profit_loss_value_jpn=params_dict.get("profit_loss_value_jpn"),
            profit_loss_ratio=params_dict.get("profit_loss_ratio"),
            eval_value=params_dict.get("eval_value"),
            eval_value_jpn=params_dict.get("eval_value_jpn"),
            created_at=params_dict.get("created_at", datetime.now().isoformat()),
            updated_at=params_dict.get("updated_at", datetime.now().isoformat())
        )


class ExchangeRate(Base):
    __tablename__ = "ExchangeRate"
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = Column(Integer, primary_key=True, autoincrement=True)
    target = Column(String(3), nullable=False)
    base = Column(String(3), nullable=False)
    rate = Column(REAL, nullable=False)
    created_at = Column(String(30), nullable=False)
    updated_at = Column(String(30), nullable=False)

    def __init__(self,
                 target,
                 base,
                 rate,
                 created_at=datetime.now().isoformat(),
                 updated_at=datetime.now().isoformat()) -> None:
        self.target = target
        self.base = base
        self.rate = rate
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "target": self.target,
            "base": self.base,
            "rate": self.rate,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def create(cls, params_dict: dict) -> "StockViewer":
        return cls(
            target=params_dict.get("target"),
            base=params_dict.get("base"),
            rate=params_dict.get("rate"),
            created_at=params_dict.get("created_at", datetime.now().isoformat()),
            updated_at=params_dict.get("updated_at", datetime.now().isoformat())
        )


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
