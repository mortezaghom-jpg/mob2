"""
موتور حسابداری. تنها بخشی از سیستم که اجازه دارد رکورد مالی واقعی و سند حسابداری بسازد.
AI هرگز مستقیم اینجا را صدا نمی‌زند؛ فقط بعد از تایید صریح کاربر (Confirmation) این ماژول اجرا می‌شود.

منطق:
- خرید نسیه: بدهکار = هزینه/کالا ، بستانکار = طرف حساب (بدهی ما به طرف حساب زیاد می‌شود)
- پرداخت: بدهکار = طرف حساب (بدهی ما کم می‌شود) ، بستانکار = تنخواه
- تسویه: معادل یک پرداخت به اندازه کل مانده حساب طرف
"""
from sqlalchemy.orm import Session

from app import models
from app.schemas import ExtractedTransaction
from app.ai.nlp_utils import today_jalali_str
from datetime import datetime, date


class AccountingError(Exception):
    pass


def _get_or_create_person(db: Session, name: str) -> models.Person:
    person = db.query(models.Person).filter(models.Person.name == name, models.Person.is_deleted == 0).first()
    if not person:
        person = models.Person(name=name, type="person", balance=0)
        db.add(person)
        db.flush()
    return person


def _get_or_create_category(db: Session, name: str | None) -> models.Category | None:
    if not name:
        return None
    cat = db.query(models.Category).filter(models.Category.name == name).first()
    if not cat:
        cat = models.Category(name=name, is_system=0)
        db.add(cat)
        db.flush()
    return cat


def _get_default_cash_account(db: Session) -> models.Account:
    acc = db.query(models.Account).filter(models.Account.id == 1).first()
    if not acc:
        acc = models.Account(id=1, name="تنخواه نقدی", type="cash", balance=0)
        db.add(acc)
        db.flush()
    return acc


def record_purchase(db: Session, parsed: ExtractedTransaction) -> models.Transaction:
    if not parsed.person_name or not parsed.amount:
        raise AccountingError("اطلاعات ضروری (طرف حساب یا مبلغ) ناقص است؛ تراکنش ثبت نشد.")

    person = _get_or_create_person(db, parsed.person_name)
    category = _get_or_create_category(db, parsed.category)

    jalali_date = parsed.jalali_date or today_jalali_str()
    utc_date = datetime.utcnow().isoformat() + "Z"

    invoice = None
    if parsed.items:
        invoice = models.Invoice(
            person_id=person.id,
            total_amount=parsed.amount,
            jalali_date=jalali_date,
            utc_date=utc_date,
            payment_status="unpaid",
        )
        db.add(invoice)
        db.flush()

    txn = models.Transaction(
        type="purchase",
        person_id=person.id,
        category_id=category.id if category else None,
        invoice_id=invoice.id if invoice else None,
        amount=parsed.amount,
        description=parsed.description,
        jalali_date=jalali_date,
        utc_date=utc_date,
        payment_method=parsed.payment_method or "credit",
        source="voice" if parsed.date_phrase is not None else "manual",
        raw_text=None,
        ai_confidence=parsed.confidence,
        status="confirmed",
    )
    db.add(txn)
    db.flush()

    for it in parsed.items:
        total_price = it.total_price or int(it.unit_price * it.quantity)
        db.add(models.TransactionItem(
            transaction_id=txn.id,
            item_name=it.item_name,
            quantity=it.quantity,
            unit_price=it.unit_price,
            total_price=total_price,
        ))

    # سند حسابداری: بدهکار = هزینه/کالا (دسته‌بندی) ، بستانکار = طرف حساب
    debit_account_name = category.name if category else "هزینه متفرقه"
    db.add(models.JournalEntry(
        transaction_id=txn.id,
        debit_account=debit_account_name,
        credit_account=person.name,
        amount=parsed.amount,
        jalali_date=jalali_date,
        utc_date=utc_date,
    ))

    # مانده حساب طرف: بدهکار ما نسبت به او افزایش می‌یابد -> balance شخص کاهش می‌یابد
    person.balance -= parsed.amount
    person.total_purchases += parsed.amount
    person.last_transaction_at = utc_date

    db.commit()
    db.refresh(txn)
    return txn


def record_payment(db: Session, parsed: ExtractedTransaction) -> models.Transaction:
    if not parsed.person_name or not parsed.amount:
        raise AccountingError("اطلاعات ضروری (طرف حساب یا مبلغ) ناقص است؛ تراکنش ثبت نشد.")

    person = _get_or_create_person(db, parsed.person_name)
    cash_account = _get_default_cash_account(db)
    category = _get_or_create_category(db, parsed.category)

    jalali_date = parsed.jalali_date or today_jalali_str()
    utc_date = datetime.utcnow().isoformat() + "Z"

    txn = models.Transaction(
        type="payment",
        person_id=person.id,
        category_id=category.id if category else None,
        amount=parsed.amount,
        description=parsed.description,
        jalali_date=jalali_date,
        utc_date=utc_date,
        payment_method=parsed.payment_method or "cash",
        source="voice",
        ai_confidence=parsed.confidence,
        status="confirmed",
    )
    db.add(txn)
    db.flush()

    # سند حسابداری: بدهکار = طرف حساب ، بستانکار = تنخواه
    db.add(models.JournalEntry(
        transaction_id=txn.id,
        debit_account=person.name,
        credit_account=cash_account.name,
        amount=parsed.amount,
        jalali_date=jalali_date,
        utc_date=utc_date,
    ))
    db.add(models.Payment(
        transaction_id=txn.id,
        person_id=person.id,
        amount=parsed.amount,
        method=parsed.payment_method or "cash",
        jalali_date=jalali_date,
        utc_date=utc_date,
    ))

    person.balance += parsed.amount
    person.total_payments += parsed.amount
    person.last_transaction_at = utc_date
    cash_account.balance -= parsed.amount

    db.commit()
    db.refresh(txn)
    return txn


def record_settlement(db: Session, person_name: str) -> models.Transaction:
    person = db.query(models.Person).filter(models.Person.name == person_name, models.Person.is_deleted == 0).first()
    if not person:
        raise AccountingError(f"طرف حسابی با نام '{person_name}' پیدا نشد.")
    if person.balance >= 0:
        raise AccountingError(f"مانده حساب {person.name} بدهکاری از سمت ما نیست (مانده: {person.balance}).")

    amount = abs(person.balance)
    cash_account = _get_default_cash_account(db)
    jalali_date = today_jalali_str()
    utc_date = datetime.utcnow().isoformat() + "Z"

    txn = models.Transaction(
        type="settlement",
        person_id=person.id,
        amount=amount,
        description=f"تسویه کامل حساب {person.name}",
        jalali_date=jalali_date,
        utc_date=utc_date,
        payment_method="cash",
        source="voice",
        status="confirmed",
    )
    db.add(txn)
    db.flush()

    db.add(models.JournalEntry(
        transaction_id=txn.id,
        debit_account=person.name,
        credit_account=cash_account.name,
        amount=amount,
        jalali_date=jalali_date,
        utc_date=utc_date,
    ))

    person.balance = 0
    person.last_transaction_at = utc_date
    cash_account.balance -= amount

    db.commit()
    db.refresh(txn)
    return txn
