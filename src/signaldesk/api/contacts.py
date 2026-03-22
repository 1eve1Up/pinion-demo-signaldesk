from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from signaldesk.api.deps import get_current_user
from signaldesk.db.session import get_async_session
from signaldesk.models import Contact, User
from signaldesk.schemas.contact import ContactCreate, ContactRead, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


async def _get_owned_contact_or_404(
    contact_id: int,
    current_user: User,
    session: AsyncSession,
) -> Contact:
    result = await session.execute(
        select(Contact).where(
            Contact.id == contact_id,
            Contact.owner_id == current_user.id,
        )
    )
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )
    return contact


@router.get("", response_model=list[ContactRead])
async def list_contacts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[Contact]:
    result = await session.execute(
        select(Contact)
        .where(Contact.owner_id == current_user.id)
        .order_by(Contact.id)
    )
    return list(result.scalars().all())


@router.post(
    "",
    response_model=ContactRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: ContactCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Contact:
    contact = Contact(owner_id=current_user.id, name=body.name)
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactRead)
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Contact:
    return await _get_owned_contact_or_404(contact_id, current_user, session)


@router.patch("/{contact_id}", response_model=ContactRead)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Contact:
    contact = await _get_owned_contact_or_404(contact_id, current_user, session)
    if body.name is not None:
        contact.name = body.name
    await session.commit()
    await session.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    contact = await _get_owned_contact_or_404(contact_id, current_user, session)
    await session.delete(contact)
    await session.commit()
