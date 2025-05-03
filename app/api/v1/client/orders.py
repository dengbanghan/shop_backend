#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: dengbanghan@gmail.com
# @Date: 2025/5/3

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.crud.order import (
    create_order, get_orders_by_user, get_order,
    cancel_order, request_refund
)
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderOut
from app.core.security import get_current_user
from app.services.order import OrderService
from app.tasks import process_payment_async

router = APIRouter()


@router.post("/orders/", response_model=OrderOut)
def create_new_order(
        order: OrderCreate,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    order_service = OrderService(db)
    try:
        # 检查库存并创建订单
        db_order = order_service.create_order_with_inventory_check(
            user_id=current_user["id"],
            order_data=order
        )

        # 异步处理支付
        process_payment_async.delay(db_order.id)

        return db_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Order creation failed")


@router.get("/orders/", response_model=List[OrderOut])
def read_user_orders(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    return get_orders_by_user(db, user_id=current_user["id"], skip=skip, limit=limit)


@router.post("/orders/{order_id}/cancel")
def cancel_user_order(
        order_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    order = get_order(db, order_id=order_id)
    if not order or order.user_id != current_user["id"]:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in [0, 1]:  # 只有已提交和待付款的订单可以取消
        raise HTTPException(status_code=400, detail="Order cannot be canceled in current status")
    cancel_order(db, order_id=order_id)
    return {"detail": "Order canceled successfully"}


@router.post("/orders/{order_id}/refund")
def request_order_refund(
        order_id: int,
        reason: str,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    order = get_order(db, order_id=order_id)
    if not order or order.user_id != current_user["id"]:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status not in [2, 3, 4, 5]:  # 只有特定状态的订单可以退款
        raise HTTPException(status_code=400, detail="Order cannot be refunded in current status")
    request_refund(db, order_id=order_id, reason=reason)
    return {"detail": "Refund requested successfully"}