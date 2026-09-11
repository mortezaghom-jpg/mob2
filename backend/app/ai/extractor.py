"""
لایه هوش مصنوعی واقعی.
این ماژول جمله فارسی خام کاربر را می‌گیرد، به مدل زبانی (OpenAI یا سازگار) می‌فرستد
و خروجی را در قالب ExtractedTransaction برمی‌گرداند.

نکات معماری:
- AI هرگز مستقیماً رکورد حسابداری تولید نمی‌کند؛ فقط JSON ساختاریافته برمی‌گرداند.
- کلید API فقط از app.config.settings خوانده می‌شود (که از .env روی سرور می‌آید) و
  هرگز داخل کد یا اپلیکیشن اندروید Hard-Code نیست.
- اگر فیلدهای ضروری (amount برای purchase/payment) وجود نداشته باشد، needs_clarification=True
  می‌شود و سیستم اصلاً تراکنش را ثبت نمی‌کند تا کاربر پاسخ دهد.
"""
import json
import re
from datetime import date

from openai import OpenAI

from app.config import settings
from app.schemas import ExtractedTransaction, ExtractedItem
from app.ai.nlp_utils import words_to_number, parse_relative_date_phrase, normalize_digits

SYSTEM_PROMPT = """تو یک استخراج‌کننده اطلاعات مالی فارسی هستی. کاربر یک جمله فارسی درباره
خرید، پرداخت، تسویه حساب یا پرسش درباره حساب‌ها می‌گوید. تو باید فقط و فقط یک JSON خروجی
بدهی، بدون هیچ توضیح اضافه، دقیقاً با این ساختار:

{
  "intent": "purchase | payment | settlement | query_balance | query_report | unknown",
  "person_name": "نام طرف حساب یا null",
  "amount": عدد صحیح تومان یا null,
  "category": "یکی از دسته‌بندی‌ها یا null",
  "description": "توضیح کوتاه یا null",
  "date_phrase": "عبارت خام تاریخ گفته‌شده مثل 'دیروز' یا 'امروز' یا null",
  "payment_method": "cash | credit | bank | null",
  "items": [ {"item_name": "...", "quantity": عدد, "unit_price": عدد} ],
  "confidence": عدد اعشاری بین 0 و 1,
  "missing_fields": ["لیست فیلدهای ضروری که مشخص نیست"],
  "clarification_question": "در صورت ابهام، یک سوال کوتاه فارسی برای کاربر، وگرنه null"
}

قوانین:
- اگر مبلغ به‌صورت کلمه فارسی گفته شده (مثل 'پنج میلیون')، آن را در amount به عدد صحیح تبدیل کن.
- برای purchase و payment، اگر amount مشخص نیست، آن را در missing_fields قرار بده و
  confidence را پایین بگذار و یک clarification_question بپرس.
- اگر جمله چند قلم کالا دارد (فاکتور)، همه را در items لیست کن و amount را جمع کل بگذار.
- برای query_balance و query_report نیازی به amount نیست.
- فقط JSON خروجی بده، بدون Markdown و بدون توضیح اضافه.
"""


def _get_client() -> OpenAI:
    return OpenAI(api_key=settings.AI_API_KEY, base_url=settings.AI_BASE_URL)


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(raw)


def call_ai_model(text: str) -> dict:
    """فراخوانی واقعی مدل AI. نیازمند AI_API_KEY معتبر در .env بک‌اند است."""
    client = _get_client()
    response = client.chat.completions.create(
        model=settings.AI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    return _extract_json(content)


def extract_transaction(text: str, today: date | None = None) -> ExtractedTransaction:
    """
    نقطه ورود اصلی: متن فارسی -> ExtractedTransaction.
    مبلغ و تاریخ نهایتاً توسط nlp_utils قطعی می‌شوند (نه توسط خود مدل)، تا خطای محاسباتی AI
    باعث ثبت اشتباه نشود.
    """
    data = call_ai_model(text)

    # مبلغ را با پارسر قطعی محلی هم دوباره چک/تصحیح می‌کنیم اگر AI عدد نداده ولی متن دارد
    amount = data.get("amount")
    if amount is None:
        amount_phrase_match = re.search(
            r"([\d۰-۹,\.]+|[یکدوسهچهارپنجششهفتهشتنه\s]+(?:هزار|میلیون|میلیارد)[\s\S]*?)(?=تومان|ریال|$)",
            text,
        )
        if amount_phrase_match:
            amount = words_to_number(amount_phrase_match.group(1))
    elif isinstance(amount, str):
        amount = words_to_number(amount)

    jalali_date, utc_date = parse_relative_date_phrase(data.get("date_phrase") or "", today)

    items = [ExtractedItem(**it) for it in data.get("items", [])]

    missing = list(data.get("missing_fields") or [])
    intent = data.get("intent", "unknown")
    if intent in ("purchase", "payment") and not amount and "amount" not in missing:
        missing.append("amount")

    needs_clarification = bool(missing) or bool(data.get("clarification_question"))

    return ExtractedTransaction(
        intent=intent,
        person_name=data.get("person_name"),
        amount=amount,
        category=data.get("category"),
        description=data.get("description"),
        date_phrase=data.get("date_phrase"),
        jalali_date=jalali_date,
        payment_method=data.get("payment_method"),
        items=items,
        confidence=float(data.get("confidence", 0.5)),
        missing_fields=missing,
        clarification_question=data.get("clarification_question"),
        needs_clarification=needs_clarification,
    )
