#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    balance: float

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    id: int
    user_id: int
    total_price: float
    status: str
    created_at: datetime

    class Config:
        orm_mode = True