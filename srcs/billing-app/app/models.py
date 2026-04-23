from sqlchemy import Column, Integer, String, create_engine
from sqlchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()


DB_URL = os.getenv("DB_URL")

db = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=db)
Base = declarative_base()


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    number_of_items = Column(String, nullable=False)
    total_amount = Column(String, nullable=False)

def init_db():
    Base.metadata.create_all(bind=db)