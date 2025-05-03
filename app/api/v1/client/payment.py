#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.payment import PaymentCreate, PaymentResult, RefundRequest
from app.services.payment import PaymentService
from app.db.session import get_db
from app.core.security import get_current_user

router = APIRouter()

@router.post("/payments/create", response_model=PaymentResult)
def create_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """创建支付"""
    service = PaymentService(db)
    try:
        result = service.process_payment(data.order_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/payments/callback/{payment_no}")
def payment_callback(
    payment_no: str,
    data: dict,
    db: Session = Depends(get_db)
):
    """支付回调接口(第三方支付平台调用)"""
    service = PaymentService(db)
    success = service.handle_payment_callback(payment_no, data)
    if success:
        return {"status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Callback processing failed")

@router.post("/payments/refund", response_model=PaymentResult)
def request_refund(
    data: RefundRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """申请退款"""
    service = PaymentService(db)
    try:
        result = service.refund(data.order_id, data.amount)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))