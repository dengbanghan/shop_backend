#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.id"), nullable=False)
    checked_out = Column(Boolean, default=False)
    checked_out_time = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart")

    def __repr__(self):
        return f"<Cart(id={self.id}, user_id={self.user_id}, checked_out={self.checked_out})>"


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    cart_id = Column(BIGINT, ForeignKey("carts.id"), nullable=False)
    product_id = Column(BIGINT, ForeignKey("products.id"), nullable=False)
    sku_id = Column(BIGINT, ForeignKey("product_skus.id"), nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    selected = Column(Boolean, default=True)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
    sku = relationship("ProductSku")

    def __repr__(self):
        return f"<CartItem(id={self.id}, product_id={self.product_id}, quantity={self.quantity})>"


# 在User模型中添加反向引用
User.carts = relationship("Cart", order_by=Cart.id.desc(), back_populates="user")