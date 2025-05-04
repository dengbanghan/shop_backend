#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

from fastapi import Request, HTTPException
from redis import Redis
import time


class RateLimiter:
    def __init__(self, redis: Redis, limit: int, window: int):
        self.redis = redis
        self.limit = limit  # 允许的请求次数
        self.window = window  # 时间窗口（秒）

    async def __call__(self, request: Request):
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"

        current = self.redis.get(key)
        if current and int(current) >= self.limit:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Limit {self.limit} per {self.window}s"
            )

        pipeline = self.redis.pipeline()
        pipeline.incr(key, 1)
        pipeline.expire(key, self.window)
        pipeline.execute()

        return True


# 初始化示例
redis_client = Redis.from_url(os.getenv("REDIS_URL"))
user_limiter = RateLimiter(redis_client, limit=100, window=60)  # 60秒100次
auth_limiter = RateLimiter(redis_client, limit=10, window=60)  # 登录接口严格限制