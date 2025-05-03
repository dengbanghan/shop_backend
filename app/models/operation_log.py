#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.dialects.mysql import BIGINT
from app.models.base import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(BIGINT, ForeignKey("users.id"), nullable=True)
    operation = Column(String(50), nullable=False)
    method = Column(String(10), nullable=False)
    path = Column(String(255), nullable=False)
    params = Column(Text, nullable=True)
    ip = Column(String(50), nullable=True)
    status_code = Column(Integer, nullable=True)
    user_agent = Column(String(255), nullable=True)

    def __repr__(self):
        return f"<OperationLog(id={self.id}, operation={self.operation}, user_id={self.user_id})>"