"""
ابزارهای پردازش زبان فارسی: تبدیل اعداد فارسی/کلمه‌ای به عدد، و تاریخ شمسی <-> میلادی.
این توابع مستقل از AI هستند (قطعی و قابل تست) و AI فقط عبارت خام را استخراج می‌کند؛
تبدیل نهایی اینجا با دقت ۱۰۰٪ انجام می‌شود (به AI برای محاسبه ریاضی/تاریخ اعتماد نمی‌کنیم).
"""
import re
from datetime import datetime, timedelta, date

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"
ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"


def normalize_digits(text: str) -> str:
    for i, d in enumerate(PERSIAN_DIGITS):
        text = text.replace(d, str(i))
    for i, d in enumerate(ARABIC_DIGITS):
        text = text.replace(d, str(i))
    return text


_NUM_WORDS = {
    "صفر": 0, "یک": 1, "دو": 2, "سه": 3, "چهار": 4, "پنج": 5, "شش": 6, "شیش": 6,
    "هفت": 7, "هشت": 8, "نه": 9, "ده": 10, "یازده": 11, "دوازده": 12, "سیزده": 13,
    "چهارده": 14, "پانزده": 15, "شانزده": 16, "هفده": 17, "هجده": 18, "نوزده": 19,
    "بیست": 20, "سی": 30, "چهل": 40, "پنجاه": 50, "شصت": 60, "هفتاد": 70,
    "هشتاد": 80, "نود": 90, "صد": 100, "دویست": 200, "سیصد": 300, "چهارصد": 400,
    "پانصد": 500, "ششصد": 600, "هفتصد": 700, "هشتصد": 800, "نهصد": 900,
}
_MULTIPLIERS = {"هزار": 1_000, "میلیون": 1_000_000, "میلیارد": 1_000_000_000}


def words_to_number(phrase: str) -> int | None:
    """تبدیل عبارت فارسی مثل 'پنج میلیون و سیصد هزار' به عدد صحیح."""
    phrase = normalize_digits(phrase).strip()
    # اگر خودش عدد رقمی است (با جداکننده هزارگان احتمالی)
    digit_match = re.fullmatch(r"[\d,\.]+", phrase.replace(" ", ""))
    if digit_match:
        return int(re.sub(r"[,\.]", "", phrase.replace(" ", "")))

    tokens = re.split(r"[\s]+|\bو\b", phrase)
    tokens = [t for t in tokens if t and t != "و"]
    if not tokens:
        return None

    total = 0
    current = 0
    matched_any = False
    for tok in tokens:
        tok = tok.strip("،")
        if tok in _NUM_WORDS:
            current += _NUM_WORDS[tok]
            matched_any = True
        elif tok in _MULTIPLIERS:
            multiplier = _MULTIPLIERS[tok]
            current = (current or 1) * multiplier
            total += current
            current = 0
            matched_any = True
        elif re.fullmatch(r"\d+", tok):
            current += int(tok)
            matched_any = True
    total += current
    return total if matched_any else None


# --- تبدیل تاریخ شمسی <-> میلادی (الگوریتم استاندارد، بدون وابستگی خارجی) ---

def gregorian_to_jalali(g_year: int, g_month: int, g_day: int):
    g_days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

    gy = g_year - 1600
    gm = g_month - 1
    gd = g_day - 1

    g_day_no = 365 * gy + (gy + 3) // 4 - (gy + 99) // 100 + (gy + 399) // 400
    for i in range(gm):
        g_day_no += g_days_in_month[i]
    if gm > 1 and ((g_year % 4 == 0 and g_year % 100 != 0) or (g_year % 400 == 0)):
        g_day_no += 1
    g_day_no += gd

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461
    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    for i in range(11):
        if j_day_no < j_days_in_month[i]:
            jm = i + 1
            jd = j_day_no + 1
            break
        j_day_no -= j_days_in_month[i]
    else:
        jm = 12
        jd = j_day_no + 1

    return jy, jm, jd


def jalali_to_gregorian(j_year: int, j_month: int, j_day: int):
    jy = j_year - 979
    jm = j_month - 1
    jd = j_day - 1

    j_day_no = 365 * jy + (jy // 33) * 8 + ((jy % 33) + 3) // 4
    j_days_in_month = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]
    for i in range(jm):
        j_day_no += j_days_in_month[i]
    j_day_no += jd
    g_day_no = j_day_no + 79

    gy = 1600 + 400 * (g_day_no // 146097)
    g_day_no %= 146097
    leap = True
    if g_day_no >= 36525:
        g_day_no -= 1
        gy += 100 * (g_day_no // 36524)
        g_day_no %= 36524
        if g_day_no >= 365:
            g_day_no += 1
        else:
            leap = False
    gy += 4 * (g_day_no // 1461)
    g_day_no %= 1461
    if g_day_no >= 366:
        leap = False
        gy += (g_day_no - 1) // 365
        g_day_no = (g_day_no - 1) % 365

    g_days_in_month = [31, 29 if ((gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0) else 28,
                        31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 0
    for i in range(12):
        if g_day_no < g_days_in_month[i]:
            gm = i + 1
            gd = g_day_no + 1
            break
        g_day_no -= g_days_in_month[i]
    return gy, gm, gd


def today_jalali_str(d: date | None = None) -> str:
    d = d or date.today()
    jy, jm, jd = gregorian_to_jalali(d.year, d.month, d.day)
    return f"{jy:04d}-{jm:02d}-{jd:02d}"


WEEKDAYS_FA = {"شنبه": 5, "یکشنبه": 6, "دوشنبه": 0, "سه شنبه": 1, "سه‌شنبه": 1,
               "چهارشنبه": 2, "پنجشنبه": 3, "پنج شنبه": 3, "جمعه": 4}


def parse_relative_date_phrase(phrase: str, base: date | None = None) -> tuple[str, str]:
    """
    عبارات نسبی فارسی مثل امروز/دیروز/پریروز/هفته قبل/اول ماه/نام روز هفته را
    به (jalali_date_str, utc_date_str) تبدیل می‌کند.
    """
    base = base or date.today()
    phrase = normalize_digits(phrase or "").strip()

    target = base
    if not phrase or phrase in ("امروز",):
        target = base
    elif phrase == "دیروز":
        target = base - timedelta(days=1)
    elif phrase == "پریروز":
        target = base - timedelta(days=2)
    elif "هفته قبل" in phrase or "هفته پیش" in phrase:
        target = base - timedelta(days=7)
    elif "اول ماه" in phrase:
        jy, jm, _ = gregorian_to_jalali(base.year, base.month, base.day)
        gy, gm, gd = jalali_to_gregorian(jy, jm, 1)
        target = date(gy, gm, gd)
    else:
        matched = False
        for wd_name, wd_idx in WEEKDAYS_FA.items():
            if wd_name in phrase:
                delta = (base.weekday() - wd_idx) % 7
                delta = delta or 7
                target = base - timedelta(days=delta)
                matched = True
                break
        if not matched:
            # تلاش برای الگوی "۱۰ شهریور" یا تاریخ رقمی مستقیم YYYY-MM-DD
            iso_match = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", phrase)
            if iso_match:
                jy, jm, jd = map(int, iso_match.groups())
                gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
                target = date(gy, gm, gd)
            else:
                months_fa = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                             "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
                day_month_match = re.match(r"(\d{1,2})\s+(\S+)", phrase)
                if day_month_match and day_month_match.group(2) in months_fa:
                    jd = int(day_month_match.group(1))
                    jm = months_fa.index(day_month_match.group(2)) + 1
                    jy, _, _ = gregorian_to_jalali(base.year, base.month, base.day)
                    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
                    target = date(gy, gm, gd)
                else:
                    target = base  # عبارت ناشناخته -> پیش‌فرض امروز

    jy, jm, jd = gregorian_to_jalali(target.year, target.month, target.day)
    jalali_str = f"{jy:04d}-{jm:02d}-{jd:02d}"
    utc_str = datetime(target.year, target.month, target.day).isoformat() + "Z"
    return jalali_str, utc_str
