import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.tables import Base

load_dotenv('./database/.env')  # take environment variables from .env.

DB_USER = os.getenv("DB_USER")
print(DB_USER)
DB_PASSWORD = os.getenv("DB_PASSWORD")
print(DB_PASSWORD)
DB_HOST = os.getenv("DB_HOST")
print(DB_HOST)
DB_NAME = os.getenv("DB_NAME")
print(DB_NAME)

# Connecting to your database with the SQLAlchemy engine
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}')
# Defining a session factory (SessionLocal) using that engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
  # supply database sessions
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


# ---Create new migration ---
# alembic revision -m "Message describing this migration"
# ----- run migrations -----
# alembic upgrade head