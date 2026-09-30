from datetime import date as DateType
from typing import Optional

from pydantic import BaseModel, ConfigDict
from models import EquipmentStatusEnum


class UserSchema(BaseModel):
    login: str
    password: str

class EquipmentAddSchema(BaseModel):
    name: str
    serial_number: str
    type_name: str
    date: DateType | None = None

class EquipmentUpdateSchema(BaseModel):
    name: Optional[str] = None
    serial_number: Optional[str] = None
    type_name: Optional[str] = None
    status: Optional[EquipmentStatusEnum] = None
    date: Optional[DateType] = None

class EquipmentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    serial_number: str
    type_name: str
    status: EquipmentStatusEnum
    user_login: str
    date: DateType | None = None