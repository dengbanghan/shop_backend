#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

from fastapi import Request, Response


class CacheControl:
    def __init__(self, max_age: int = 60):
        self.max_age = max_age

    async def __call__(self, request: Request, call_next):
        response: Response = await call_next(request)

        # 跳过非GET请求
        if request.method != "GET":
            return response

        # 设置缓存头
        cache_control = f"public, max-age={self.max_age}"
        response.headers["Cache-Control"] = cache_control
        response.headers["ETag"] = generate_etag(response.body)
        return response


def generate_etag(data: bytes) -> str:
    import hashlib
    return hashlib.md5(data).hexdigest()