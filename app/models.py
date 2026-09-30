from datetime import date as DateType
from app.database import Base
from sqlalchemy import String, ForeignKey, DateTime, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum


class EquipmentStatusEnum(enum.Enum):
    RELIABLY = "Исправно"
    REPAIR = "Требует ремонта"
    DEBITED = "Списано"

class User(Base):
    __tablename__ = "users"

    login: Mapped[str] = mapped_column(String(50), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

class Equipment(Base):
    __tablename__ = "equipment"
    __table_args__ = (UniqueConstraint("user_login", "inv_number", "serial_number", name="equipment_serial_number"),)
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    inv_number: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False)
    type_id: Mapped[int] = mapped_column(ForeignKey("equipment_types.id"), nullable=False)
    status: Mapped[EquipmentStatusEnum] = mapped_column(Enum(EquipmentStatusEnum), nullable=False, default=EquipmentStatusEnum.RELIABLY)
    user_login: Mapped[str] = mapped_column(ForeignKey("users.login"))
    date: Mapped[DateType] = mapped_column(DateTime, nullable=False)
    type: Mapped["EquipmentType"] = relationship(back_populates="equipment_items")

class EquipmentType(Base):
    __tablename__ = "equipment_types"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_login: Mapped[str|None] = mapped_column(ForeignKey("users.login"))
    equipment_items: Mapped[list["Equipment"]] = relationship(back_populates="type")