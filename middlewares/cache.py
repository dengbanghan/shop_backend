#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(status_code=403, detail="Invalid authentication scheme")
        return self.verify_jwt(credentials.credentials)

    @staticmethod
    def verify_jwt(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET_KEY"),
                algorithms=[os.getenv("JWT_ALGORITHM")]
            )
            if payload.get("exp") < datetime.utcnow().timestamp():
                raise HTTPException(status_code=403, detail="Token expired")
            return payload
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")


def role_required(required_roles: list):
    def decorator(endpoint):
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user
            if user["role"] not in required_roles:
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
            return await endpoint(request, *args, **kwargs)

        return wrapper

    return decorator