# Backend - حساب‌یار هوشمند تنخواه

## نصب و اجرا

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # ویندوز: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# سپس .env را باز کنید و AI_API_KEY واقعی خودتان را قرار دهید

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

بعد از اجرا:
- مستندات تعاملی API: http://localhost:8000/docs
- تست سلامت: http://localhost:8000/health

## اجرای تست‌های واحد (بدون نیاز به AI API / اینترنت)

```bash
pip install pytest
python -m pytest tests/ -v
```

این تست‌ها منطق قطعی تبدیل عدد فارسی و تاریخ شمسی را چک می‌کنند (بدون فراخوانی AI واقعی).

## اندپوینت‌های اصلی

| Method | Path | توضیح |
|---|---|---|
| POST | /voice/parse | متن فارسی -> AI -> JSON ساختاریافته + پیام تایید |
| POST | /voice/confirm | ثبت نهایی تراکنش بعد از تایید کاربر |
| GET | /transactions | لیست تراکنش‌ها |
| GET | /persons | لیست طرف‌حساب‌ها |
| GET | /reports/dashboard | آمار داشبورد |
| GET | /reports/category-summary | جمع هزینه به تفکیک دسته‌بندی |

## امنیت

- `AI_API_KEY` فقط در فایل `.env` روی سرور است و هرگز به کلاینت اندروید ارسال نمی‌شود.
- در Production حتماً `ALLOWED_ORIGINS` را محدود کنید و پشت HTTPS (مثلاً با Nginx/Caddy) قرار دهید.
