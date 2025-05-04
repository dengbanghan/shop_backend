#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware


def apply_security_middlewares(app):
    # 强制HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)

    # 可信主机
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["example.com", "*.example.com"]
    )

    # CORS
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# 请求体大小限制
async def body_size_limit_middleware(request: Request, call_next):
    max_size = 1024 * 1024  # 1MB
    body = await request.body()
    if len(body) > max_size:
        raise APIError(413, "Request body too large")
    request.state.body = body
    return await call_next(request)