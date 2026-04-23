import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, Numeric, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


def build_database_url():
    configured_url = os.getenv("BILLING_DB_URL")
    if configured_url:
        return configured_url

    user = os.getenv("BILLING_DB_USER", "billing_user")
    password = os.getenv("BILLING_DB_PASSWORD", "billing_pass")
    host = os.getenv("BILLING_DB_HOST", "localhost")
    port = os.getenv("BILLING_DB_PORT", "5432")
    database = os.getenv("BILLING_DB_NAME", "billing_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


DATABASE_URL = build_database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False)
    number_of_items = Column(Integer, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)


def init_db():
    Base.metadata.create_all(bind=engine)
