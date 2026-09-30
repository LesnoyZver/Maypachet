from datetime import date as DateType, date
from typing import Optional, List, Literal

from fastapi import HTTPException
from sqlalchemy import select, or_, desc, asc, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Equipment, EquipmentType, Base, EquipmentStatusEnum
from schemas import EquipmentAddSchema, EquipmentUpdateSchema
from exceptions import *


class EquipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_equipment(self, login: str,
                                     id: Optional[int],
                                     name: Optional[str],
                                     serial_number: Optional[str],
                                     type_name: Optional[str],
                                     status: Optional[EquipmentStatusEnum],
                                     sort_by: Literal["date", "id"],
                                     order: Literal["asc", "desc"])-> List[tuple[Equipment, str]]:
        conditions = []
        if id:
            conditions.append(Equipment.id == id)
        if name:
            conditions.append(Equipment.name.ilike(f"%{name}%"))
        if serial_number:
            conditions.append(Equipment.serial_number.ilike(f"%{serial_number}%"))
        if type_name:
            res = await self.session.execute(select(EquipmentType.id).where(EquipmentType.name==type_name))
            type_id = res.scalar_one_or_none()
            if type_id is None:
                return []
            conditions.append(Equipment.type_id == type_id)
        if status:
            conditions.append(Equipment.status == status)
        sort_column = {"date": Equipment.date, "id": Equipment.id}[sort_by]
        order_func = desc if order  == "desc" else asc
        result = await self.session.execute(select(Equipment, EquipmentType.name)
                                            .join(EquipmentType, Equipment.type_id == EquipmentType.id)
                                            .where(Equipment.user_login==login, *conditions)
                                            .order_by(order_func(sort_column)))
        equipments = result.all()
        return equipments

    async def add_equipment(self, login: str, data: EquipmentAddSchema):
        try:
            if data.date > date.today():
                raise InvalidDateError("Invalid date")
            type_id = await self.get_or_add_type(login, data.type_name)
            next_inv_number = await self.session.execute(
                select(func.coalesce(func.max(Equipment.inv_number), 0) + 1)
                .where(Equipment.user_login == login)
            )
            inv_number = next_inv_number.scalar_one()
            equipment = Equipment(
                inv_number=inv_number,
                name=data.name,
                serial_number=data.serial_number,
                type_id=type_id,
                user_login=login,
                date=data.date or DateType.today(),
            )
            self.session.add(equipment)
            await self.session.commit()
            return equipment
        except InvalidDateError:
            raise HTTPException(status_code=400, detail="Invalid date")

    async def get_or_add_type(self, user_login: str, type_name: str) -> int:
        type_obj = await self.session.scalar(
            select(EquipmentType).where(
                EquipmentType.name == type_name,
                or_(EquipmentType.user_login.is_(None), EquipmentType.user_login == user_login),
            )
        )
        if type_obj is not None:
            return type_obj.id
        new_type_obj = EquipmentType(name=type_name, user_login=user_login)
        self.session.add(new_type_obj)
        await self.session.commit()
        return new_type_obj.id

    async def get_equipment_types(self, login: str) -> List[EquipmentType]:
        result = await self.session.execute(
            select(EquipmentType)
            .where(or_(EquipmentType.user_login.is_(None), EquipmentType.user_login == login))
            .order_by(EquipmentType.name)
        )
        return result.scalars().all()

    async def update_equipment(self, login: str, inv_number: int, equipment: EquipmentUpdateSchema):
        try:
            if equipment.date is not None and equipment.date > date.today():
                raise InvalidDateError("Invalid date")

            equip = await self.session.scalar(
                select(Equipment).where(
                    Equipment.user_login == login,
                    Equipment.inv_number == inv_number,
                )
            )
            if equip is None:
                raise HTTPException(status_code=404, detail="Equipment not found")

            if equipment.type_name is not None:
                type_id = await self.get_or_add_type(login, equipment.type_name)
                equip.type_id = type_id

            update_data = equipment.model_dump(exclude={"type_name"}, exclude_unset=True)
            for field, value in update_data.items():
                setattr(equip, field, value)

            await self.session.commit()
            return equip
        except InvalidDateError:
            raise HTTPException(status_code=400, detail="Invalid date")