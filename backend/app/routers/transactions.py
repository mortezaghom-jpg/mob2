from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List

from app.database import get_db
from app.schemas import TransactionOut, PersonOut
from app import models

router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=List[TransactionOut])
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    return (db.query(models.Transaction)
            .order_by(desc(models.Transaction.id))
            .limit(limit).all())


@router.get("/transactions/{txn_id}", response_model=TransactionOut)
def get_transaction(txn_id: int, db: Session = Depends(get_db)):
    txn = db.query(models.Transaction).get(txn_id)
    if not txn:
        raise HTTPException(404, "تراکنش پیدا نشد.")
    return txn


@router.get("/persons", response_model=List[PersonOut])
def list_persons(db: Session = Depends(get_db)):
    return db.query(models.Person).filter(models.Person.is_deleted == 0).all()


@router.get("/persons/{person_id}", response_model=PersonOut)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(models.Person).get(person_id)
    if not person:
        raise HTTPException(404, "طرف حساب پیدا نشد.")
    return person
