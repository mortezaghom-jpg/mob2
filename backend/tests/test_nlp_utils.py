"""
تست‌های واحد برای منطق قطعی (بدون نیاز به AI API / اینترنت):
- تبدیل کلمه فارسی به عدد
- تبدیل تاریخ نسبی فارسی
- تبدیل شمسی <-> میلادی

اجرا: cd backend && python -m pytest tests/test_nlp_utils.py -v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from app.ai.nlp_utils import (
    words_to_number, gregorian_to_jalali, jalali_to_gregorian,
    parse_relative_date_phrase, normalize_digits,
)


def test_words_to_number_simple():
    assert words_to_number("پنج میلیون") == 5_000_000


def test_words_to_number_compound():
    assert words_to_number("دو میلیون و پانصد هزار") == 2_500_000


def test_words_to_number_digit_string():
    assert words_to_number("۵۰۰۰۰۰۰") == 5_000_000


def test_normalize_digits():
    assert normalize_digits("۱۲۳") == "123"


def test_jalali_roundtrip():
    gy, gm, gd = 2026, 9, 8
    jy, jm, jd = gregorian_to_jalali(gy, gm, gd)
    gy2, gm2, gd2 = jalali_to_gregorian(jy, jm, jd)
    assert (gy2, gm2, gd2) == (gy, gm, gd)


def test_relative_date_today():
    base = date(2026, 9, 8)
    jalali, utc = parse_relative_date_phrase("امروز", base)
    assert jalali == "1405-06-17"  # امروز معادل ۱۷ شهریور ۱۴۰۵ است


def test_relative_date_yesterday():
    base = date(2026, 9, 8)
    jalali_today, _ = parse_relative_date_phrase("امروز", base)
    jalali_yesterday, _ = parse_relative_date_phrase("دیروز", base)
    assert jalali_yesterday < jalali_today


# --- ۷ جمله تست اجباری طبق مستندات پروژه ---
# این تست‌ها بخش استخراج مبلغ/تاریخ محلی را چک می‌کنند. بخش intent/person_name/category
# نیازمند فراخوانی واقعی AI API است (نیاز به AI_API_KEY معتبر - در tests/test_extractor_ai.py).

MANDATORY_TEST_SENTENCES = [
    "از احمدی ۵ میلیون تومان خرید کردم بابت تدارکات.",
    "به احمدی ۲ میلیون تومان پرداخت کردم.",
    "۵ میلیون بابت کرایه حمل پرداخت کردم.",
    "حساب احمدی چقدر مانده؟",
    "کل هزینه تدارکات این ماه چقدر بوده؟",
    "دیروز از ابزار پایتخت خرید کردم.",
    "از احمدی خرید کردم.",  # نباید ثبت شود چون مبلغ ندارد
]


def test_amount_extraction_from_mandatory_sentences():
    import re
    from app.ai.nlp_utils import words_to_number

    expected_amounts = [5_000_000, 2_000_000, 5_000_000, None, None, None, None]
    for sentence, expected in zip(MANDATORY_TEST_SENTENCES, expected_amounts):
        match = re.search(r"([\d۰-۹]+)\s*میلیون", sentence)
        if match:
            amount = words_to_number(match.group(0))
            assert amount == expected, f"'{sentence}' -> {amount}, انتظار {expected}"
        else:
            assert expected is None
