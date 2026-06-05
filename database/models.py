from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    dm_id = Column(Integer, ForeignKey("users.id"))

    # Зв'язки для зручного доступу з коду
    dungeon_master = relationship("User", backref="campaigns")
    characters = relationship("Character", back_populates="campaign")


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    race = Column(String(50), nullable=False)
    char_class = Column(String(50), nullable=False)
    level = Column(Integer, default=1)

    # Зовнішні ключі: кому належить і в якій він кампанії
    player_id = Column(Integer, ForeignKey("users.id"))
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))

    # Зв'язки
    player = relationship("User", backref="characters")
    campaign = relationship("Campaign", back_populates="characters")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    # Зберігаємо назви та описи двома мовами прямо в таблиці
    name_en = Column(String(100), nullable=False)
    name_uk = Column(String(100), nullable=False)
    description_en = Column(Text, nullable=True)
    description_uk = Column(Text, nullable=True)

    rarity = Column(String(50), default="common")  # Звичайна, рідкісна, легендарна
    price = Column(Integer, default=0)  # Ціна в золотих монетах


class StatusEffect(Base):
    __tablename__ = "status_effects"

    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(100), nullable=False)
    name_uk = Column(String(100), nullable=False)
    description_en = Column(Text, nullable=True)
    description_uk = Column(Text, nullable=True)

    is_positive = Column(Integer, default=0)  # 1 для бафів, 0 для дебафів/хвороб