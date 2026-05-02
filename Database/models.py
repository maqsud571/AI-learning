from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from Database.database import Base


# =========================
# 🚗 CARS TABLE
# =========================
class Car(Base):
    """
    🚗 cars table
    - mashinalar haqida ma'lumot
    """
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    brand = Column(String)
    color = Column(String)
    price = Column(Float)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# 📚 BOOKS TABLE
# =========================
class Book(Base):
    """
    📚 books table
    - kitoblar ma'lumotlari
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# ✏️ STATIONERY TABLE
# =========================
class Stationery(Base):
    """
    ✏️ stationery table
    - ofis buyumlari
    """
    __tablename__ = "stationery"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# 🏗 CONSTRUCTION TABLE
# =========================
class Construction(Base):
    """
    🏗 construction table
    - qurilish materiallari
    """
    __tablename__ = "construction"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)