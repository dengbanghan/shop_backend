#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base


class OrderLog(Base):
    __tablename__ = "order_logs"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    order_id = Column(BIGINT, ForeignKey("orders.id"), nullable=False)
    action = Column(String(50), nullable=False)
    operator_id = Column(BIGINT, nullable=True)  # 用户ID或管理员ID
    operator_type = Column(Integer, nullable=False)  # 1-用户, 2-管理员, 3-系统
    operator_name = Column(String(50), nullable=True)
    note = Column(Text, nullable=True)
    ip_address = Column(String(50), nullable=True)

    order = relationship("Order", back_populates="logs")

    def __repr__(self):
        return f"<OrderLog(id={self.id}, order_id={self.order_id}, action={self.action})>"


# 在Order模型中添加反向引用
Order.logs = relationship("OrderLog", order_by=OrderLog.id, back_populates="order")