from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models
from app.ai.nlp_utils import today_jalali_str

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    cash = db.query(models.Account).filter(models.Account.id == 1).first()
    total_purchases = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.type == "purchase").scalar()
    total_payments = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.type == "payment").scalar()

    debtors = db.query(models.Person).filter(models.Person.balance < 0).all()   # ما به آن‌ها بدهکاریم
    creditors = db.query(models.Person).filter(models.Person.balance > 0).all()  # آن‌ها به ما بدهکارند

    today = today_jalali_str()
    today_expenses = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.jalali_date == today, models.Transaction.type == "purchase").scalar()

    month_prefix = today[:7]  # YYYY-MM
    month_expenses = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
        models.Transaction.jalali_date.like(f"{month_prefix}%"), models.Transaction.type == "purchase").scalar()

    recent = (db.query(models.Transaction).order_by(models.Transaction.id.desc()).limit(10).all())

    return {
        "tanakhah_balance": cash.balance if cash else 0,
        "total_purchases": total_purchases,
        "total_payments": total_payments,
        "our_debt_to_others": sum(abs(p.balance) for p in debtors),
        "others_debt_to_us": sum(p.balance for p in creditors),
        "today_expenses": today_expenses,
        "month_expenses": month_expenses,
        "recent_transactions": [
            {"id": t.id, "type": t.type, "amount": t.amount, "jalali_date": t.jalali_date,
             "description": t.description} for t in recent
        ],
    }


@router.get("/category-summary")
def category_summary(db: Session = Depends(get_db)):
    rows = (db.query(models.Category.name, func.coalesce(func.sum(models.Transaction.amount), 0))
            .join(models.Transaction, models.Transaction.category_id == models.Category.id)
            .group_by(models.Category.name)
            .order_by(func.sum(models.Transaction.amount).desc())
            .all())
    return [{"category": name, "total": total} for name, total in rows]
