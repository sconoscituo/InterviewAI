from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.payment import create_payment, confirm_payment

router = APIRouter(prefix="/api/payments", tags=["payments"])


class PaymentOut(BaseModel):
    id: int
    amount: int
    currency: str
    status: str
    plan: str
    tx_id: str

    class Config:
        from_attributes = True


class ConfirmBody(BaseModel):
    tx_id: str


@router.post("/checkout", response_model=PaymentOut, status_code=201)
async def checkout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.is_premium:
        raise HTTPException(status_code=400, detail="이미 프리미엄 사용자입니다.")
    payment = await create_payment(current_user.id, db)
    return payment


@router.post("/confirm", response_model=PaymentOut)
async def confirm(
    body: ConfirmBody,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = await confirm_payment(body.tx_id, db)
    if not payment:
        raise HTTPException(status_code=404, detail="결제 정보를 찾을 수 없습니다.")
    return payment
