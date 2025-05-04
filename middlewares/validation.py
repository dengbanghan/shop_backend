#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

from pydantic import BaseModel, ValidationError
from fastapi import Request

def validate_request(schema: BaseModel):
    async def decorator(request: Request):
        try:
            data = await request.json()
            validated = schema(**data)
            request.state.validated_data = validated
            return validated
        except ValidationError as e:
            raise APIError(400, str(e.errors()))
    return decorator

# 使用示例
class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str

@router.post("/users")
@validate_request(UserCreateSchema)
async def create_user(request: Request):
    data = request.state.validated_data
    # 处理数据...