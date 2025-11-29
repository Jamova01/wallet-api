from sqlmodel import Session, select

from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash


def create_first_superuser(session: Session) -> None:
    """
    Create the first superuser in the database if it does not exist.
    """
    statement = select(User).where(User.email == settings.FIRST_SUPERUSER)
    existing_user = session.exec(statement).first()

    if existing_user:
        return

    hashed_password = get_password_hash(settings.FIRST_SUPERUSER_PASSWORD)

    superuser = User(
        email=settings.FIRST_SUPERUSER,
        hashed_password=hashed_password,
        full_name="Superuser",
        is_active=True,
        is_superuser=True,
    )

    session.add(superuser)
    session.commit()
    session.refresh(superuser)
