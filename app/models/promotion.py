#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime
from enum import IntEnum


class PromotionType(IntEnum):
    DISCOUNT = 1  # 折扣
    FULL_REDUCTION = 2  # 满减
    COUPON = 3  # 优惠券


class PromotionStatus(IntEnum):
    NOT_STARTED = 0  # 未开始
    ONGOING = 1  # 进行中
    ENDED = 2  # 已结束
    DISABLED = 3  # 已禁用


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(PromotionType), nullable=False)
    status = Column(Enum(PromotionStatus), default=PromotionStatus.NOT_STARTED)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    # 通用字段
    is_active = Column(Boolean, default=True)
    created_by = Column(BIGINT, ForeignKey("users.id"), nullable=True)
    # 折扣相关
    discount_rate = Column(Numeric(5, 2), nullable=True)  # 折扣率(0.1-1.0)
    # 满减相关
    full_amount = Column(Numeric(10, 2), nullable=True)  # 满多少
    reduce_amount = Column(Numeric(10, 2), nullable=True)  # 减多少

    products = relationship("PromotionProduct", back_populates="promotion")
    coupons = relationship("Coupon", back_populates="promotion")

    def __repr__(self):
        return f"<Promotion(id={self.id}, name={self.name}, type={self.type.name})>"

    @property
    def is_valid(self):
        now = datetime.now()
        return (self.is_active and
                self.status == PromotionStatus.ONGOING and
                self.start_time <= now <= self.end_time)


class PromotionProduct(Base):
    __tablename__ = "promotion_products"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    promotion_id = Column(BIGINT, ForeignKey("promotions.id"), nullable=False)
    product_id = Column(BIGINT, ForeignKey("products.id"), nullable=False)

    promotion = relationship("Promotion", back_populates="products")
    product = relationship("Product", back_populates="promotions")

    def __repr__(self):
        return f"<PromotionProduct(id={self.id}, promotion_id={self.promotion_id}, product_id={self.product_id})>"


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    promotion_id = Column(BIGINT, ForeignKey("promotions.id"), nullable=False)
    user_id = Column(BIGINT, ForeignKey("users.id"), nullable=True)  # 指定用户
    discount_amount = Column(Numeric(10, 2), nullable=False)
    min_order_amount = Column(Numeric(10, 2), default=0)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    used_time = Column(DateTime, nullable=True)

    promotion = relationship("Promotion", back_populates="coupons")
    user = relationship("User", back_populates="coupons")

    def __repr__(self):
        return f"<Coupon(id={self.id}, code={self.code}, discount_amount={self.discount_amount})>"


# 在Product模型中添加反向引用
Product.promotions = relationship("PromotionProduct", back_populates="product")

# 在User模型中添加反向引用
User.coupons = relationship("Coupon", back_populates="user")