"""
قرارداد داده‌ای بین AI و بقیه سیستم.
هوش مصنوعی *فقط* این ساختار را تولید می‌کند و هرگز مستقیم رکورد حسابداری نمی‌سازد.
معماری: Voice -> STT -> AI -> این Schema -> Validation -> Confirmation -> Accounting Engine -> DB
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class ExtractedItem(BaseModel):
    item_name: str
    quantity: float = 1
    unit_price: int
    total_price: Optional[int] = None


class ExtractedTransaction(BaseModel):
    """خروجی ساختاریافته‌ای که مدل AI باید تولید کند."""
    intent: str  # purchase | payment | settlement | query_balance | query_report | unknown
    person_name: Optional[str] = None
    amount: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date_phrase: Optional[str] = None       # عبارت خام تاریخ مثل "دیروز"، "۱۰ شهریور"
    jalali_date: Optional[str] = None       # بعد از تبدیل توسط nlp_utils
    payment_method: Optional[str] = None    # cash | credit | bank
    items: List[ExtractedItem] = Field(default_factory=list)

    confidence: float = 0.0
    missing_fields: List[str] = Field(default_factory=list)
    clarification_question: Optional[str] = None
    needs_clarification: bool = False


class VoiceParseRequest(BaseModel):
    text: str  # متن حاصل از Speech-to-Text یا تایپ مستقیم کاربر


class VoiceParseResponse(BaseModel):
    parsed: ExtractedTransaction
    confirmation_message: str


class TransactionConfirmRequest(BaseModel):
    parsed: ExtractedTransaction
    confirmed: bool = True


class TransactionOut(BaseModel):
    id: int
    type: str
    person_id: Optional[int]
    amount: int
    description: Optional[str]
    jalali_date: str
    utc_date: str
    status: str

    class Config:
        from_attributes = True


class PersonOut(BaseModel):
    id: int
    name: str
    type: str
    balance: int
    total_purchases: int
    total_payments: int
    last_transaction_at: Optional[str]

    class Config:
        from_attributes = True
