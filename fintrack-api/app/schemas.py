from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TransactionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=60)
    kind: Literal["income", "expense"]
    transaction_date: date = Field(default_factory=date.today)

    @field_validator("title", "category")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

class TransactionRead(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class Summary(BaseModel):
    total_income: float
    total_expenses: float
    balance: float
