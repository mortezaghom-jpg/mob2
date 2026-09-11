from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import VoiceParseRequest, VoiceParseResponse, TransactionConfirmRequest, TransactionOut
from app.ai.extractor import extract_transaction
from app.accounting import engine as accounting_engine
from app import models

router = APIRouter(prefix="/voice", tags=["voice"])


def _build_confirmation_message(parsed) -> str:
    if parsed.needs_clarification:
        if parsed.clarification_question:
            return parsed.clarification_question
        missing_fa = {"amount": "مبلغ", "person_name": "طرف حساب"}
        missing = "، ".join(missing_fa.get(m, m) for m in parsed.missing_fields)
        return f"اطلاعات ناقص است ({missing}). لطفاً کامل بگویید."

    if parsed.intent == "purchase":
        return (f"نوع: خرید\nطرف حساب: {parsed.person_name}\n"
                f"مبلغ: {parsed.amount:,} تومان\nدسته‌بندی: {parsed.category or 'نامشخص'}\n"
                f"تاریخ: {parsed.jalali_date}\nاین تراکنش ثبت شود؟ بله / خیر")
    if parsed.intent == "payment":
        return (f"نوع: پرداخت\nطرف حساب: {parsed.person_name}\n"
                f"مبلغ: {parsed.amount:,} تومان\nتاریخ: {parsed.jalali_date}\n"
                f"این تراکنش ثبت شود؟ بله / خیر")
    if parsed.intent == "settlement":
        return f"تسویه کامل حساب {parsed.person_name} ثبت شود؟ بله / خیر"
    return "درخواست شما دریافت شد."


@router.post("/parse", response_model=VoiceParseResponse)
def parse_voice_text(payload: VoiceParseRequest, db: Session = Depends(get_db)):
    """
    مرحله ۱: متن (از STT یا تایپ) -> AI -> Structured JSON -> پیام تاییدیه برای کاربر.
    هنوز چیزی در دیتابیس ثبت نمی‌شود.
    """
    parsed = extract_transaction(payload.text)

    log = models.AiLog(
        raw_text=payload.text,
        parsed_json=parsed.model_dump_json(),
        confidence=parsed.confidence,
        needs_clarification=int(parsed.needs_clarification),
    )
    db.add(log)
    db.commit()

    return VoiceParseResponse(parsed=parsed, confirmation_message=_build_confirmation_message(parsed))


@router.post("/confirm", response_model=TransactionOut)
def confirm_transaction(payload: TransactionConfirmRequest, db: Session = Depends(get_db)):
    """
    مرحله ۲: بعد از پاسخ 'بله' کاربر، Accounting Engine واقعاً رکورد را ثبت می‌کند.
    """
    if not payload.confirmed:
        raise HTTPException(status_code=400, detail="تراکنش توسط کاربر لغو شد.")

    parsed = payload.parsed
    if parsed.needs_clarification:
        raise HTTPException(status_code=422, detail="اطلاعات ناقص است؛ نمی‌توان ثبت کرد.")

    try:
        if parsed.intent == "purchase":
            txn = accounting_engine.record_purchase(db, parsed)
        elif parsed.intent == "payment":
            txn = accounting_engine.record_payment(db, parsed)
        elif parsed.intent == "settlement":
            txn = accounting_engine.record_settlement(db, parsed.person_name)
        else:
            raise HTTPException(status_code=400, detail="این نوع درخواست قابل ثبت به‌عنوان تراکنش نیست.")
    except accounting_engine.AccountingError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return txn
