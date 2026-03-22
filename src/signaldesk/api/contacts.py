from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from signaldesk.api.deps import get_current_user
from signaldesk.db.session import get_async_session
from signaldesk.models import Contact, Note, User
from signaldesk.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from signaldesk.schemas.note import NoteCreate, NoteRead, NoteUpdate

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


async def _get_owned_note_or_404(
    contact_id: int,
    note_id: int,
    current_user: User,
    session: AsyncSession,
) -> Note:
    await _get_owned_contact_or_404(contact_id, current_user, session)
    result = await session.execute(
        select(Note).where(Note.id == note_id, Note.contact_id == contact_id)
    )
    note = result.scalar_one_or_none()
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    return note


@router.get("", response_model=list[ContactRead])
async def list_contacts(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[Contact]:
    result = await session.execute(
        select(Contact).where(Contact.owner_id == current_user.id).order_by(Contact.id)
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
    contact = Contact(
        owner_id=current_user.id,
        name=body.name,
        email=body.email,
        phone=body.phone,
        company=body.company,
    )
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
    update = body.model_dump(exclude_unset=True)
    if "name" in update and update["name"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="name cannot be set to null",
        )
    for key, value in update.items():
        setattr(contact, key, value)
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


@router.get("/{contact_id}/notes", response_model=list[NoteRead])
async def list_notes(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> list[Note]:
    await _get_owned_contact_or_404(contact_id, current_user, session)
    result = await session.execute(
        select(Note).where(Note.contact_id == contact_id).order_by(Note.id)
    )
    return list(result.scalars().all())


@router.post(
    "/{contact_id}/notes",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_note(
    contact_id: int,
    body: NoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Note:
    await _get_owned_contact_or_404(contact_id, current_user, session)
    note = Note(
        contact_id=contact_id,
        body=body.body,
        interaction_type=body.interaction_type,
        occurred_at=body.occurred_at,
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


@router.get("/{contact_id}/notes/{note_id}", response_model=NoteRead)
async def get_note(
    contact_id: int,
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Note:
    return await _get_owned_note_or_404(contact_id, note_id, current_user, session)


@router.patch("/{contact_id}/notes/{note_id}", response_model=NoteRead)
async def update_note(
    contact_id: int,
    note_id: int,
    body: NoteUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> Note:
    note = await _get_owned_note_or_404(contact_id, note_id, current_user, session)
    update = body.model_dump(exclude_unset=True)
    if "body" in update and update["body"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="body cannot be set to null",
        )
    for key, value in update.items():
        setattr(note, key, value)
    await session.commit()
    await session.refresh(note)
    return note


@router.delete(
    "/{contact_id}/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_note(
    contact_id: int,
    note_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> None:
    note = await _get_owned_note_or_404(contact_id, note_id, current_user, session)
    await session.delete(note)
    await session.commit()
