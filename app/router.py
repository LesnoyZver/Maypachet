from fastapi import APIRouter, Depends, Response, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal

from app.auth import Auth
from app.schemas import EquipmentUpdateSchema
from auth import Auth, security, get_user_login
from database import get_session
from models import EquipmentStatusEnum
from service import EquipmentService
from schemas import UserSchema, EquipmentAddSchema, EquipmentSchema


async def get_equipment_service(session: AsyncSession = Depends(get_session)) -> EquipmentService:
    equipment_service = EquipmentService(session)
    return equipment_service


router = APIRouter()


@router.post("/auth/register", tags=["auth"])
async def register_user(registration_data: UserSchema,
                        session: AsyncSession = Depends(get_session)):
    auth = Auth(session)
    res = await auth.register_user(login=registration_data.login, password=registration_data.password)
    return res

@router.post("/auth/login", tags=["auth"])
async def login_user(login_data: UserSchema,
                     response: Response,
                     session: AsyncSession = Depends(get_session)):
    auth = Auth(session)
    res = await auth.auth_user(login_data.login, login_data.password)
    security.set_access_cookies(res, response)
    return {"login": login_data.login}

@router.post("/auth/logout", tags=["auth"], dependencies=[security.ACCESS_REQUIRED])
async def logout_user(response: Response):
    security.unset_cookies(response)
    return {"message": "Logged out"}

@router.post("/equipment/change_password", tags=["equipment"])
async def change_user_password(password: str,
                               new_password: str,
                               login: str = Depends(get_user_login),
                               session: AsyncSession = Depends(get_session)):
    auth = Auth(session)
    await auth.change_user_password(login, password, new_password)
    return {"message": "Password changed successfully"}

@router.post("/equipment/add", tags=["equipment"])
async def add_equipment(data: EquipmentAddSchema,
                        login: str = Depends(get_user_login),
                        service: EquipmentService = Depends(get_equipment_service)):
    equipment = await service.add_equipment(login, data)
    return {"id": equipment.id}

@router.get("/equipment", tags=["equipment"])
async def get_equipment(id: Optional[int] = Query(default=None),
                                name: Optional[str] = Query(default=None),
                                serial_number: Optional[str] = Query(default=None),
                                type_name: Optional[str] = Query(default=None),
                                status: Optional[EquipmentStatusEnum] = Query(default=None),
                                 sort_by: Literal["date", "id"] = Query(default="date"),
                                 order: Literal["asc", "desc"] = Query(default="asc"),
                                login: str = Depends(get_user_login),
                                service: EquipmentService = Depends(get_equipment_service)):
    result = await service.get_all_equipment(id=id,
                                             name=name,
                                             serial_number=serial_number,
                                             type_name=type_name,
                                             status=status,
                                             login=login,
                                             sort_by=sort_by,
                                             order=order)
    return {"equipment": [
        EquipmentSchema(
            id=equipment.inv_number,
            name=equipment.name,
            serial_number=equipment.serial_number,
            type_name=type_name,
            status=equipment.status,
            user_login=equipment.user_login,
            date=equipment.date
        )
        for equipment, type_name in result]
    }

@router.get("/equipment-types", tags=["equipment"])
async def get_equipment_types(login: str = Depends(get_user_login),
                              service: EquipmentService = Depends(get_equipment_service)):
    types = await service.get_equipment_types(login)
    return {"types": [t.name for t in types]}

@router.post("/equipment/changes", tags=["equipment"])
async def change_equipment(equipment: EquipmentUpdateSchema,
                           inv_number: int,
                           login: str = Depends(get_user_login),
                           service: EquipmentService = Depends(get_equipment_service)):
    result = await service.update_equipment(login, inv_number, equipment)
    return result