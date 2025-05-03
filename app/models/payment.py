#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Numeric, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base
from enum import IntEnum


class PaymentStatus(IntEnum):
    PENDING = 0  # 待支付
    SUCCESS = 1  # 支付成功
    FAILED = 2  # 支付失败
    REFUNDED = 3  # 已退款
    CLOSED = 4  # 已关闭


class PaymentMethod(IntEnum):
    WECHAT = 1  # 微信支付
    ALIPAY = 2  # 支付宝
    JDPAY = 3  # 京东支付


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_id = Column(BIGINT, ForeignKey("orders.id"), nullable=False)
    payment_no = Column(String(32), unique=True, nullable=False)  # 支付系统流水号
    transaction_id = Column(String(64), nullable=True)  # 第三方支付交易号
    method = Column(Enum(PaymentMethod), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    paid_time = Column(DateTime, nullable=True)
    payment_info = Column(Text, nullable=True)  # 支付信息(JSON)
    refund_amount = Column(Numeric(10, 2), default=0)
    refund_time = Column(DateTime, nullable=True)
    callback_time = Column(DateTime, nullable=True)
    callback_content = Column(Text, nullable=True)

    order = relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, amount={self.amount}, status={self.status.name})>"


# 在Order模型中添加反向引用
Order.payment = relationship("Payment", uselist=False, back_populates="order")