#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text
from sqlalchemy.dialects.mysql import BIGINT
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), unique=True, nullable=True)
    wechat_openid = Column(String(100), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    # 会员信息
    membership_level = Column(Integer, default=1)
    membership_expires_at = Column(DateTime, nullable=True)
    # 其他信息
    bio = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"