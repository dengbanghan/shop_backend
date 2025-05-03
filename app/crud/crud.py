#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy.orm import Session
from app.models import models
from app.schemas import schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_product(db: Session, product: schemas.ProductCreate, owner_id: int):
    db_product = models.Product(**product.dict(), owner_id=owner_id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Product).offset(skip).limit(limit).all()


def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    # 获取商品信息
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        return None

    # 计算总价
    total_price = product.price * order.quantity

    # 创建订单
    db_order = models.Order(
        user_id=user_id,
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        status="completed"
    )

    # 更新库存
    product.stock -= order.quantity

    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_user_orders(db: Session, user_id: int):
    return db.query(models.Order).filter(models.Order.user_id == user_id).all()