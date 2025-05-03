#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Numeric, Text, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base
from enum import IntEnum


class OrderStatus(IntEnum):
    SUBMITTED = 0  # 已提交
    PENDING_PAYMENT = 1  # 待付款
    PAID = 2  # 已付款
    PENDING_SHIPMENT = 3  # 待发货
    SHIPPED = 4  # 已发货
    RECEIVED = 5  # 已收货
    REFUNDING = 6  # 退款中
    RETURNING = 7  # 退货中
    EXCHANGING = 8  # 换货中
    COMPLETED = 9  # 已完成
    CANCELLED = 10  # 已取消


class PaymentMethod(IntEnum):
    WECHAT = 1  # 微信支付
    ALIPAY = 2  # 支付宝
    JDPAY = 3  # 京东支付


class Order(Base):
    __tablename__ = "orders"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_no = Column(String(32), unique=True, nullable=False)
    user_id = Column(BIGINT, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    shipping_fee = Column(Numeric(10, 2), default=0)
    payment_method = Column(Enum(PaymentMethod), nullable=True)
    payment_time = Column(DateTime, nullable=True)
    payment_transaction_id = Column(String(100), nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.SUBMITTED)
    shipping_address_id = Column(BIGINT, ForeignKey("user_addresses.id"), nullable=True)
    shipping_address = Column(Text, nullable=False)
    shipping_company = Column(String(50), nullable=True)
    shipping_number = Column(String(50), nullable=True)
    shipping_time = Column(DateTime, nullable=True)
    receive_time = Column(DateTime, nullable=True)
    note = Column(Text, nullable=True)
    # 发票信息
    invoice_needed = Column(Boolean, default=False)
    invoice_title = Column(String(100), nullable=True)
    invoice_content = Column(String(100), nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    address = relationship("Address")

    def __repr__(self):
        return f"<Order(id={self.id}, order_no={self.order_no}, status={self.status.name})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_id = Column(BIGINT, ForeignKey("orders.id"), nullable=False)
    product_id = Column(BIGINT, ForeignKey("products.id"), nullable=False)
    sku_id = Column(BIGINT, ForeignKey("product_skus.id"), nullable=True)
    product_name = Column(String(100), nullable=False)
    product_image = Column(String(255), nullable=True)
    sku_attributes = Column(String(255), nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2), nullable=True)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    refund_status = Column(Integer, default=0)  # 0-无退款, 1-退款中, 2-已退款

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    sku = relationship("ProductSku")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, product_name={self.product_name}, quantity={self.quantity})>"


# 在User模型中添加反向引用
User.orders = relationship("Order", order_by=Order.id.desc(), back_populates="user")