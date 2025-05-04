    #!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

    from fastapi import Request
    from fastapi.responses import JSONResponse
    import traceback


    class APIError(Exception):
        def __init__(self, code: int, message: str):
            self.code = code
            self.message = message


    async def global_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, APIError):
            return JSONResponse(
                status_code=exc.code,
                content={"code": exc.code, "message": exc.message}
            )

        # 记录未处理异常
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "Internal server error"}
        )