from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import settings

class Base(DeclarativeBase):
    pass

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    try:
        from . import models  # noqa
        Base.metadata.create_all(bind=engine)
    except Exception:
        # The app can still run in API-only mode if PostgreSQL is not available.
        pass
