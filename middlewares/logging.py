#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/5

import logging
from fastapi import Request
from datetime import datetime


class RequestLogger:
    def __init__(self):
        self.logger = logging.getLogger("api")
        self.logger.setLevel(logging.INFO)

    async def __call__(self, request: Request, call_next):
        start_time = datetime.now()
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "process_time": process_time,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }

        self.logger.info(log_data)
        return response