#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from celery import Celery
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.payment import PaymentService
import time

celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery.task(bind=True)
def process_payment_async(self, order_id):
    db = SessionLocal()
    try:
        payment_service = PaymentService(db)
        payment_service.process_payment(order_id)
    except Exception as e:
        # 重试逻辑
        raise self.retry(exc=e, countdown=60, max_retries=3)
    finally:
        db.close()