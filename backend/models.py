# backend/models.py
from pydantic import BaseModel, validator
from datetime import date
from typing import Optional
import re


# For displaying/fetching receipts
class Receipt(BaseModel):
    vendor: str
    date: Optional[date]
    amount: float
    category: str
    currency: Optional[str] = "INR"

    @validator('amount')
    def amount_positive(cls, value):
        if value <= 0:
            raise ValueError("Amount must be positive.")
        return value

    @validator('currency')
    def currency_format(cls, value):
        if not re.match(r"^[A-Z]{3}$", value):
            raise ValueError("Currency must be a 3-letter code like INR, USD, etc.")
        return value

# Model for saving corrected receipt data from the UI.(used in /save-corrected/)
class CorrectedReceipt(BaseModel):
    vendor: str
    date: Optional[date]
    amount: float
    category: str
    currency: Optional[str] = "INR"