#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from app.models.base import Base


class Address(Base):
    __tablename__ = "user_addresses"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.id"), nullable=False)
    recipient_name = Column(String(50), nullable=False)
    recipient_phone = Column(String(20), nullable=False)
    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    detailed_address = Column(String(255), nullable=False)
    postal_code = Column(String(20), nullable=True)
    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"<Address(id={self.id}, user_id={self.user_id}, {self.province}{self.city}{self.district})>"


# 在User模型中添加反向引用
User.addresses = relationship("Address", order_by=Address.id, back_populates="user")