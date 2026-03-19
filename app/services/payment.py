import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.payment import Payment
from app.models.user import User
from app.config import settings


async def create_payment(user_id: int, db: AsyncSession) -> Payment:
    payment = Payment(
        user_id=user_id,
        amount=settings.PREMIUM_MONTHLY_PRICE,
        currency="KRW",
        status="pending",
        plan="premium",
        tx_id=str(uuid.uuid4()),
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def confirm_payment(tx_id: str, db: AsyncSession) -> Payment:
    result = await db.execute(select(Payment).where(Payment.tx_id == tx_id))
    payment = result.scalar_one_or_none()
    if not payment:
        return None
    payment.status = "completed"

    user_result = await db.execute(select(User).where(User.id == payment.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_premium = True

    await db.commit()
    await db.refresh(payment)
    return payment
