# from pydantic import BaseModel

# class CarCreate(BaseModel):
#     brand: str
#     model: str
#     color: str
#     year: int
#     quantity: int

# class CarResponse(CarCreate):
#     id: int

#     class Config:
#         from_attributes = True
        
# class Qalesan(BaseModel):
#     brand: str
#     color: str
#     year: int
#     quantity: int

from pydantic import BaseModel
from typing import Optional

class CarBase(BaseModel):
    brand: str
    model: str
    color: Optional[str]
    year: Optional[int]
    price: Optional[float]
    quantity: int


class CarCreate(CarBase):
    pass


class CarResponse(CarBase):
    id: int

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    title: str
    author: Optional[str]
    genre: Optional[str]
    price: Optional[float]
    quantity: int


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int

    class Config:
        from_attributes = True


class StationeryBase(BaseModel):
    name: str
    brand: Optional[str]
    price: Optional[float]
    quantity: int


class StationeryCreate(StationeryBase):
    pass


class StationeryResponse(StationeryBase):
    id: int

    class Config:
        from_attributes = True


class ConstructionBase(BaseModel):
    name: str
    material: Optional[str]
    price: Optional[float]
    quantity: int


class ConstructionCreate(ConstructionBase):
    pass


class ConstructionResponse(ConstructionBase):
    id: int

    class Config:
        from_attributes = True

