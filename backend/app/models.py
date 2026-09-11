from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, default="person")
    phone = Column(String)
    city = Column(String)
    description = Column(Text)
    balance = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    total_payments = Column(Integer, default=0)
    last_transaction_at = Column(String)
    is_deleted = Column(Integer, default=0)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    is_system = Column(Integer, default=0)


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String)


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    balance = Column(Integer, default=0)


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    total_amount = Column(Integer, default=0)
    jalali_date = Column(String, nullable=False)
    utc_date = Column(String, nullable=False)
    payment_status = Column(String, default="unpaid")


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)  # purchase | payment | settlement
    person_id = Column(Integer, ForeignKey("persons.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    amount = Column(Integer, nullable=False)
    description = Column(Text)
    jalali_date = Column(String, nullable=False)
    utc_date = Column(String, nullable=False)
    payment_method = Column(String)
    source = Column(String, default="manual")
    raw_text = Column(Text)
    ai_confidence = Column(Float)
    status = Column(String, default="confirmed")

    items = relationship("TransactionItem", cascade="all, delete-orphan", backref="transaction")


class TransactionItem(Base):
    __tablename__ = "transaction_items"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"))
    item_name = Column(String, nullable=False)
    quantity = Column(Float, default=1)
    unit_price = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    debit_account = Column(String, nullable=False)
    credit_account = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    jalali_date = Column(String, nullable=False)
    utc_date = Column(String, nullable=False)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    method = Column(String)
    jalali_date = Column(String, nullable=False)
    utc_date = Column(String, nullable=False)


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(String)


class AiLog(Base):
    __tablename__ = "ai_logs"
    id = Column(Integer, primary_key=True)
    raw_text = Column(Text, nullable=False)
    parsed_json = Column(Text)
    confidence = Column(Float)
    needs_clarification = Column(Integer, default=0)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
