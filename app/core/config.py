#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Shop Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # 数据库配置
    SQLALCHEMY_DATABASE_URI: str = "mysql+pymysql://user:password@localhost:3306/shop"
    SQLALCHEMY_ECHO: bool = False

    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # Elasticsearch配置
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # 微信支付配置
    WECHAT_APPID: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_API_KEY: str = ""
    WECHAT_NOTIFY_URL: str = ""
    WECHAT_CERT_PATH: str = ""
    WECHAT_KEY_PATH: str = ""

    # 支付宝配置
    ALIPAY_APPID: str = ""
    ALIPAY_PRIVATE_KEY: str = ""
    ALIPAY_PUBLIC_KEY: str = ""
    ALIPAY_NOTIFY_URL: str = ""

    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()