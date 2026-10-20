from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import Transaction
from .schemas import Summary, TransactionCreate, TransactionRead

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="FinTrack API",
    description="A learning project for finance transactions, validation, filtering, and summaries.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/transactions", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    transaction = Transaction(**payload.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/transactions", response_model=list[TransactionRead])
def list_transactions(
    kind: str | None = Query(default=None, pattern="^(income|expense)$"),
    category: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = select(Transaction)
    if kind:
        query = query.where(Transaction.kind == kind)
    if category:
        query = query.where(Transaction.category.ilike(f"%{category}%"))
    query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
    return list(db.scalars(query.offset(offset).limit(limit)).all())

@app.get("/transactions/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    item = db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return item

@app.put("/transactions/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: int, payload: TransactionCreate, db: Session = Depends(get_db)):
    item = db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    item = db.get(Transaction, transaction_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(item)
    db.commit()

@app.get("/summary", response_model=Summary)
def get_summary(db: Session = Depends(get_db)):
    rows = db.scalars(select(Transaction)).all()
    income = round(sum(row.amount for row in rows if row.kind == "income"), 2)
    expenses = round(sum(row.amount for row in rows if row.kind == "expense"), 2)
    return Summary(total_income=income, total_expenses=expenses, balance=round(income-expenses, 2))
