#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.crud.product import (
    get_product, get_products, create_product,
    update_product, delete_product
)
from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductOut, ProductUpdate
from app.core.security import get_current_admin_user

router = APIRouter()

@router.post("/products/", response_model=ProductOut)
def create_new_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    return create_product(db=db, product=product)

@router.get("/products/", response_model=List[ProductOut])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    products = get_products(db, skip=skip, limit=limit, category_id=category_id)
    return products

@router.put("/products/{product_id}", response_model=ProductOut)
def update_existing_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return update_product(db=db, product_id=product_id, product=product)

@router.delete("/products/{product_id}")
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    db_product = get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    delete_product(db=db, product_id=product_id)
    return {"detail": "Product deleted successfully"}