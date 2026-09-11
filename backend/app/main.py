from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routers import voice, transactions, reports
from app import models  # noqa: F401  (لازم برای رجیستر شدن مدل‌ها قبل از create_all)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="حساب‌یار هوشمند تنخواه - Backend",
    description="Voice -> STT -> AI -> Structured JSON -> Validation -> Confirmation -> Accounting Engine -> DB",
    version="0.1.0-MVP",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice.router)
app.include_router(transactions.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}
